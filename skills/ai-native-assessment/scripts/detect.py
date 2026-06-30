#!/usr/bin/env python3
"""Deterministic AI-native assessment scanner.

Scans a repository and outputs JSON for language probes, command synthesis,
monorepo detection, additional scans, and evidence-rich category signals.
Deterministic category scoring is available as an opt-in mode.

Usage: python scripts/detect.py [repo_root] [--with-scoring]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

VERSION = "1.0.0"

SKIP_DIRS = frozenset(
    [
        "node_modules",
        ".git",
        "dist",
        "build",
        "__pycache__",
        ".venv",
        "vendor",
        "target",
        ".next",
        ".worktrees",
    ]
)

PRIORITY_ORDER = {
    "user_override": 0,
    "explicit_script": 1,
    "framework_target": 2,
    "config_file": 3,
    "workflow": 4,
    "dependency_fallback": 5,
    "language_default": 6,
    "ai_inferred": 7,
}

SOURCE_TYPE_BY_PRIORITY = {
    "user_override": "user_override",
    "explicit_script": "script_entry",
    "framework_target": "framework_target",
    "config_file": "config",
    "workflow": "workflow",
    "dependency_fallback": "dependency",
    "language_default": "manifest_default",
    "ai_inferred": "ai_inferred",
}

CATEGORY_WEIGHTS = {
    1: 0.20,
    2: 0.25,
    3: 0.15,
    4: 0.15,
    5: 0.10,
    6: 0.15,
}


# ---------------------------------------------------------------------------
# Infrastructure
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic AI-native assessment scanner"
    )
    parser.add_argument(
        "repo_root", nargs="?", default=".", help="Path to repository root"
    )
    parser.add_argument(
        "--with-scoring",
        action="store_true",
        help="Include deterministic category scores and recommended actions",
    )
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    if not root.is_dir():
        error_exit(f"Not a directory: {root}")
    args.repo_root = root
    return args


def error_exit(msg: str, code: int = 1) -> None:
    json.dump({"error": msg}, sys.stderr)
    sys.stderr.write("\n")
    sys.exit(code)


def read_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return None
    except Exception:
        return None


def parse_apm_manifest(root: Path, tree: Set[str]) -> Dict[str, Any]:
    """Parse simple APM manifest structure for remote skills and MCP entries."""
    result = {
        "present": False,
        "skills": [],
        "security_skills": [],
        "mcp_entries": 0,
        "scripts": set(),
    }
    apm_path: Optional[str] = None
    if tree_has(tree, "apm.yml"):
        apm_path = "apm.yml"
    elif tree_has(tree, "apm.yaml"):
        apm_path = "apm.yaml"
    if not apm_path:
        return result

    content = read_text(root / apm_path)
    if not content:
        return result

    result["present"] = True
    in_scripts = False
    in_apm_deps = False
    in_mcp_deps = False
    script_indent: Optional[int] = None
    dep_indent: Optional[int] = None

    for raw_line in content.split("\n"):
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped == "scripts:" or stripped.startswith("scripts:"):
            in_scripts = True
            in_apm_deps = False
            in_mcp_deps = False
            script_indent = indent
            dep_indent = None
            continue
        if stripped == "dependencies:" or stripped.startswith("dependencies:"):
            in_scripts = False
            in_apm_deps = False
            in_mcp_deps = False
            script_indent = None
            dep_indent = None
            continue
        if stripped == "apm:" or stripped.startswith("apm:"):
            in_apm_deps = True
            in_mcp_deps = False
            in_scripts = False
            dep_indent = indent
            continue
        if stripped == "mcp:" or stripped.startswith("mcp:"):
            in_mcp_deps = True
            in_apm_deps = False
            in_scripts = False
            dep_indent = indent
            continue

        if (
            in_scripts
            and script_indent is not None
            and indent <= script_indent
            and not stripped.startswith("- ")
        ):
            in_scripts = False
        if (
            (in_apm_deps or in_mcp_deps)
            and dep_indent is not None
            and indent <= dep_indent
            and not stripped.startswith("- ")
        ):
            in_apm_deps = False
            in_mcp_deps = False

        if in_scripts and ":" in stripped and not stripped.startswith("- "):
            key = stripped.split(":", 1)[0].strip()
            if key:
                result["scripts"].add(key)
            continue

        if in_apm_deps and stripped.startswith("- "):
            dep = stripped[2:].strip().strip("'\"")
            if dep and not dep.startswith("#"):
                result["skills"].append(dep)
                dep_lower = dep.lower()
                if any(
                    kw in dep_lower
                    for kw in ["security", "codeguard", "vulnerability", "sast"]
                ):
                    result["security_skills"].append(dep)
            continue

        if in_mcp_deps and stripped.startswith("- "):
            result["mcp_entries"] += 1

    return result


def build_tree(root: Path) -> Set[str]:
    """Build set of relative paths from root, skipping SKIP_DIRS."""
    paths: Set[str] = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            rel_dir = ""
        for f in filenames:
            if rel_dir:
                paths.add(f"{rel_dir}/{f}")
            else:
                paths.add(f)
        for d in dirnames:
            if rel_dir:
                paths.add(f"{rel_dir}/{d}/")
            else:
                paths.add(f"{d}/")
    return paths


def tree_has(tree: Set[str], path: str) -> bool:
    return path in tree


def tree_has_dir(tree: Set[str], path: str) -> bool:
    if not path.endswith("/"):
        path = path + "/"
    return path in tree or any(p.startswith(path) for p in tree)


def tree_glob(tree: Set[str], pattern: str) -> List[str]:
    """Simple glob matching against tree paths."""
    import fnmatch

    return sorted(p for p in tree if fnmatch.fnmatch(p, pattern))


# ---------------------------------------------------------------------------
# Inline TOML parser (minimal, enough for pyproject.toml)
# ---------------------------------------------------------------------------


def parse_toml(content: str) -> Dict[str, Any]:
    """Minimal TOML parser for pyproject.toml files."""
    try:
        import tomllib

        return tomllib.loads(content)
    except ImportError:
        pass
    # Fallback inline parser for Python 3.9-3.10
    return _parse_toml_fallback(content)


def _parse_toml_fallback(content: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    current_section: Optional[List[str]] = None
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith("#"):
            continue
        # Section header
        m = re.match(r"^\[([^\]]+)\]$", line)
        if m:
            current_section = m.group(1).split(".")
            _ensure_section(result, current_section)
            continue
        # Array of tables
        m = re.match(r"^\[\[([^\]]+)\]\]$", line)
        if m:
            current_section = m.group(1).split(".")
            parent = (
                _ensure_section(result, current_section[:-1])
                if len(current_section) > 1
                else result
            )
            key = current_section[-1]
            if key not in parent:
                parent[key] = []
            parent[key].append({})
            continue
        # Key-value
        m = re.match(r"^([A-Za-z0-9_\-]+)\s*=\s*(.+)$", line)
        if m:
            key = m.group(1)
            val_str = m.group(2).strip()
            # Handle multiline arrays
            if val_str.startswith("[") and "]" not in val_str:
                while i < len(lines) and "]" not in val_str:
                    val_str += " " + lines[i].strip()
                    i += 1
            # Handle multiline strings
            if val_str.startswith('"""') or val_str.startswith("'''"):
                quote = val_str[:3]
                if val_str.count(quote) >= 2:
                    pass  # single line
                else:
                    while i < len(lines) and quote not in lines[i]:
                        val_str += "\n" + lines[i]
                        i += 1
                    if i < len(lines):
                        val_str += "\n" + lines[i]
                        i += 1
            value = _parse_toml_value(val_str)
            section = (
                _get_section(result, current_section) if current_section else result
            )
            if isinstance(section, list):
                section[-1][key] = value
            else:
                section[key] = value
    return result


def _ensure_section(d: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    current = d
    for k in keys:
        if k not in current:
            current[k] = {}
        val = current[k]
        if isinstance(val, list):
            current = val[-1]
        else:
            current = val
    return current


def _get_section(d: Dict[str, Any], keys: Optional[List[str]]) -> Any:
    if not keys:
        return d
    current: Any = d
    for k in keys:
        if isinstance(current, dict):
            if k not in current:
                current[k] = {}
            current = current[k]
        elif isinstance(current, list):
            current = current[-1].get(k, {})
    return current


def _parse_toml_value(s: str) -> Any:
    s = s.strip()
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1].replace('\\"', '"')
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    if s.startswith('"""') and s.endswith('"""'):
        return s[3:-3]
    if s.startswith("'''") and s.endswith("'''"):
        return s[3:-3]
    if s == "true":
        return True
    if s == "false":
        return False
    if s.startswith("["):
        return _parse_toml_array(s)
    if s.startswith("{"):
        return _parse_toml_inline_table(s)
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def _parse_toml_array(s: str) -> List[Any]:
    s = s.strip()
    if s == "[]":
        return []
    inner = s[1:-1].strip()
    items: List[Any] = []
    current = ""
    depth = 0
    in_str = False
    str_char = ""
    for ch in inner:
        if in_str:
            current += ch
            if ch == str_char:
                in_str = False
            continue
        if ch in ('"', "'"):
            in_str = True
            str_char = ch
            current += ch
        elif ch == "[":
            depth += 1
            current += ch
        elif ch == "]":
            depth -= 1
            current += ch
        elif ch == "," and depth == 0:
            val = current.strip()
            if val:
                items.append(_parse_toml_value(val))
            current = ""
        else:
            current += ch
    val = current.strip()
    if val:
        items.append(_parse_toml_value(val))
    return items


def _parse_toml_inline_table(s: str) -> Dict[str, Any]:
    s = s.strip()
    if s == "{}":
        return {}
    inner = s[1:-1].strip()
    result: Dict[str, Any] = {}
    for part in inner.split(","):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            result[k.strip()] = _parse_toml_value(v.strip())
    return result


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------


@dataclass
class ToolCandidate:
    command: str
    kind: str  # lint/test/build/format/typecheck
    priority: str
    source: str
    language: str

    def priority_num(self) -> int:
        return PRIORITY_ORDER.get(self.priority, 99)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command": self.command,
            "priority": self.priority,
            "source": self.source,
            "language": self.language,
        }


@dataclass
class ScanCandidate:
    command: str
    source: str
    label: str
    kind: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Language & Package Manager Detection
# ---------------------------------------------------------------------------


def detect_languages(root: Path, tree: Set[str]) -> List[str]:
    langs: List[str] = []
    if tree_has(tree, "package.json"):
        langs.append("node")
    if (
        tree_has(tree, "pyproject.toml")
        or tree_has(tree, "setup.py")
        or tree_has(tree, "requirements.txt")
    ):
        langs.append("python")
    if tree_has(tree, "Cargo.toml"):
        langs.append("rust")
    if tree_has(tree, "go.mod"):
        langs.append("go")
    if (
        tree_has(tree, "pom.xml")
        or tree_has(tree, "build.gradle")
        or tree_has(tree, "build.gradle.kts")
    ):
        langs.append("java_kotlin")
    if any(p.endswith(".csproj") for p in tree) or any(
        p.endswith(".sln") for p in tree
    ):
        langs.append("dotnet")
    return langs


def detect_node_pkg_mgr(tree: Set[str]) -> str:
    if tree_has(tree, "pnpm-lock.yaml"):
        return "pnpm"
    if tree_has(tree, "yarn.lock"):
        return "yarn"
    if tree_has(tree, "bun.lockb") or tree_has(tree, "bun.lock"):
        return "bun"
    return "npm"


def detect_python_pkg_mgr(tree: Set[str]) -> str:
    if tree_has(tree, "poetry.lock"):
        return "poetry"
    if tree_has(tree, "pdm.lock"):
        return "pdm"
    if tree_has(tree, "uv.lock"):
        return "uv"
    return "pip"


def detect_package_managers(langs: List[str], tree: Set[str]) -> Dict[str, str]:
    mgrs: Dict[str, str] = {}
    if "node" in langs:
        mgrs["node"] = detect_node_pkg_mgr(tree)
    if "python" in langs:
        mgrs["python"] = detect_python_pkg_mgr(tree)
    return mgrs


def detect_monorepo(root: Path, tree: Set[str]) -> Optional[Dict[str, Any]]:
    if tree_has(tree, "nx.json"):
        projects = []
        for p in tree:
            if p.endswith("project.json") and p.count("/") <= 4:
                proj_dir = os.path.dirname(p)
                if proj_dir:
                    projects.append(proj_dir)
        return {"framework": "nx", "projects": sorted(projects)}
    if tree_has(tree, "turbo.json"):
        return {"framework": "turbo", "projects": []}
    if any(
        p == ".moon/workspace.yml" or p.startswith(".moon/workspace.yml") for p in tree
    ):
        return {"framework": "moon", "projects": []}
    return None


# ---------------------------------------------------------------------------
# Per-Language Probes
# ---------------------------------------------------------------------------


def node_exec_command(pkg_mgr: str) -> str:
    if pkg_mgr == "pnpm":
        return "pnpm exec"
    if pkg_mgr == "yarn":
        return "yarn"
    if pkg_mgr == "bun":
        return "bun x"
    return "npx"


def probe_node(root: Path, tree: Set[str], pkg_mgr: str) -> List[ToolCandidate]:
    candidates: List[ToolCandidate] = []
    pkg_path = root / "package.json"
    content = read_text(pkg_path)
    if not content:
        return candidates
    try:
        pkg = json.loads(content)
    except (json.JSONDecodeError, ValueError):
        return candidates

    scripts = pkg.get("scripts", {})
    exec_cmd = node_exec_command(pkg_mgr)

    # Explicit scripts
    script_map = {
        "lint": "lint",
        "test": "test",
        "build": "build",
        "format": "format",
        "typecheck": "typecheck",
        "type-check": "typecheck",
    }
    for script_name, kind in script_map.items():
        if script_name in scripts:
            run_cmd = (
                f"{pkg_mgr} run {script_name}"
                if pkg_mgr != "npm"
                else f"npm run {script_name}"
            )
            candidates.append(
                ToolCandidate(
                    command=run_cmd,
                    kind=kind,
                    priority="explicit_script",
                    source=f"package.json scripts.{script_name}",
                    language="node",
                )
            )

    # Dependencies
    deps = set()
    for dep_key in ("dependencies", "devDependencies"):
        deps.update(pkg.get(dep_key, {}).keys())

    dep_probes = [
        ("eslint", [("lint", f"{exec_cmd} eslint .")]),
        (
            "@biomejs/biome",
            [
                ("lint", f"{exec_cmd} biome check ."),
                ("format", f"{exec_cmd} biome format ."),
            ],
        ),
        (
            "biome",
            [
                ("lint", f"{exec_cmd} biome check ."),
                ("format", f"{exec_cmd} biome format ."),
            ],
        ),
        ("prettier", [("format", f"{exec_cmd} prettier --check .")]),
        ("typescript", [("typecheck", f"{exec_cmd} tsc --noEmit")]),
        ("vitest", [("test", f"{exec_cmd} vitest run")]),
        ("jest", [("test", f"{exec_cmd} jest")]),
    ]
    for dep_name, mappings in dep_probes:
        if dep_name in deps:
            for kind, cmd in mappings:
                candidates.append(
                    ToolCandidate(
                        command=cmd,
                        kind=kind,
                        priority="dependency_fallback",
                        source=f"package.json dependency {dep_name}",
                        language="node",
                    )
                )

    # Framework targets
    if "nx" in deps and tree_has(tree, "nx.json"):
        for p in tree:
            if p.endswith("project.json") and p.count("/") <= 4:
                proj_content = read_text(root / p)
                if proj_content:
                    try:
                        proj = json.loads(proj_content)
                        targets = proj.get("targets", {})
                        for target_name in targets:
                            kind_map = {
                                "lint": "lint",
                                "test": "test",
                                "build": "build",
                                "format": "format",
                                "typecheck": "typecheck",
                            }
                            if target_name in kind_map:
                                proj_name = proj.get("name", os.path.dirname(p))
                                candidates.append(
                                    ToolCandidate(
                                        command=f"nx run {proj_name}:{target_name}",
                                        kind=kind_map[target_name],
                                        priority="framework_target",
                                        source=f"{p} targets.{target_name}",
                                        language="node",
                                    )
                                )
                    except (json.JSONDecodeError, ValueError):
                        pass

    if "turbo" in deps and tree_has(tree, "turbo.json"):
        for kind in ["lint", "test", "build", "format", "typecheck"]:
            candidates.append(
                ToolCandidate(
                    command=f"turbo run {kind}",
                    kind=kind,
                    priority="framework_target",
                    source="turbo.json",
                    language="node",
                )
            )

    if "@moonrepo/cli" in deps or "moon" in deps:
        for kind in ["lint", "test", "build", "format", "typecheck"]:
            candidates.append(
                ToolCandidate(
                    command=f"moon run {kind}",
                    kind=kind,
                    priority="framework_target",
                    source="moon workspace",
                    language="node",
                )
            )

    return candidates


def probe_python(root: Path, tree: Set[str], pkg_mgr: str) -> List[ToolCandidate]:
    candidates: List[ToolCandidate] = []
    toml_path = root / "pyproject.toml"
    toml_data: Dict[str, Any] = {}
    if tree_has(tree, "pyproject.toml"):
        content = read_text(toml_path)
        if content:
            try:
                toml_data = parse_toml(content)
            except Exception:
                pass

    tool = toml_data.get("tool", {})

    # Tool sections
    if "ruff" in tool:
        candidates.append(
            ToolCandidate(
                "ruff check .",
                "lint",
                "dependency_fallback",
                "pyproject.toml [tool.ruff]",
                "python",
            )
        )
        candidates.append(
            ToolCandidate(
                "ruff format .",
                "format",
                "dependency_fallback",
                "pyproject.toml [tool.ruff]",
                "python",
            )
        )
    if "flake8" in tool:
        candidates.append(
            ToolCandidate(
                "flake8",
                "lint",
                "dependency_fallback",
                "pyproject.toml [tool.flake8]",
                "python",
            )
        )
    if "pytest" in tool or "pytest.ini_options" in tool:
        candidates.append(
            ToolCandidate(
                "pytest",
                "test",
                "dependency_fallback",
                "pyproject.toml [tool.pytest]",
                "python",
            )
        )
    if "mypy" in tool:
        candidates.append(
            ToolCandidate(
                "mypy .",
                "typecheck",
                "dependency_fallback",
                "pyproject.toml [tool.mypy]",
                "python",
            )
        )
    if "black" in tool:
        candidates.append(
            ToolCandidate(
                "black .",
                "format",
                "dependency_fallback",
                "pyproject.toml [tool.black]",
                "python",
            )
        )
    if "pyright" in tool or "basedpyright" in tool:
        candidates.append(
            ToolCandidate(
                "pyright",
                "typecheck",
                "dependency_fallback",
                "pyproject.toml [tool.pyright]",
                "python",
            )
        )

    # Project scripts
    project = toml_data.get("project", {})
    project_scripts = project.get("scripts", {})
    for script_name, script_val in project_scripts.items():
        lower = script_name.lower()
        for keyword, kind in [
            ("lint", "lint"),
            ("test", "test"),
            ("format", "format"),
            ("build", "build"),
        ]:
            if keyword in lower:
                candidates.append(
                    ToolCandidate(
                        script_name,
                        kind,
                        "explicit_script",
                        f"pyproject.toml [project.scripts].{script_name}",
                        "python",
                    )
                )
                break

    # Check requirements.txt for deps
    if tree_has(tree, "requirements.txt"):
        req_content = read_text(root / "requirements.txt")
        if req_content:
            req_lower = req_content.lower()
            if "ruff" in req_lower and "ruff" not in tool:
                candidates.append(
                    ToolCandidate(
                        "ruff check .",
                        "lint",
                        "dependency_fallback",
                        "requirements.txt ruff",
                        "python",
                    )
                )
                candidates.append(
                    ToolCandidate(
                        "ruff format .",
                        "format",
                        "dependency_fallback",
                        "requirements.txt ruff",
                        "python",
                    )
                )
            if "pytest" in req_lower and "pytest" not in tool:
                candidates.append(
                    ToolCandidate(
                        "pytest",
                        "test",
                        "dependency_fallback",
                        "requirements.txt pytest",
                        "python",
                    )
                )
            if "mypy" in req_lower and "mypy" not in tool:
                candidates.append(
                    ToolCandidate(
                        "mypy .",
                        "typecheck",
                        "dependency_fallback",
                        "requirements.txt mypy",
                        "python",
                    )
                )

    # Build
    build_system = toml_data.get("build-system", {})
    if build_system:
        candidates.append(
            ToolCandidate(
                "python -m build",
                "build",
                "language_default",
                "pyproject.toml [build-system]",
                "python",
            )
        )

    return candidates


def probe_rust(root: Path, tree: Set[str]) -> List[ToolCandidate]:
    return [
        ToolCandidate("cargo clippy", "lint", "language_default", "Cargo.toml", "rust"),
        ToolCandidate("cargo test", "test", "language_default", "Cargo.toml", "rust"),
        ToolCandidate("cargo build", "build", "language_default", "Cargo.toml", "rust"),
        ToolCandidate(
            "cargo fmt --check", "format", "language_default", "Cargo.toml", "rust"
        ),
        ToolCandidate(
            "cargo check", "typecheck", "language_default", "Cargo.toml", "rust"
        ),
    ]


def probe_go(root: Path, tree: Set[str]) -> List[ToolCandidate]:
    candidates: List[ToolCandidate] = []
    if tree_has(tree, ".golangci.yml") or tree_has(tree, ".golangci.yaml"):
        config_file = (
            ".golangci.yml" if tree_has(tree, ".golangci.yml") else ".golangci.yaml"
        )
        candidates.append(
            ToolCandidate("golangci-lint run", "lint", "config_file", config_file, "go")
        )
    candidates.append(
        ToolCandidate("go test ./...", "test", "language_default", "go.mod", "go")
    )
    candidates.append(
        ToolCandidate("go build ./...", "build", "language_default", "go.mod", "go")
    )
    candidates.append(
        ToolCandidate("gofmt -l .", "format", "language_default", "go.mod", "go")
    )
    return candidates


def probe_java_kotlin(root: Path, tree: Set[str]) -> List[ToolCandidate]:
    candidates: List[ToolCandidate] = []
    is_maven = tree_has(tree, "pom.xml")
    is_gradle = tree_has(tree, "build.gradle") or tree_has(tree, "build.gradle.kts")

    if is_maven:
        mvn = "./mvnw" if tree_has(tree, "mvnw") else "mvn"
        candidates.append(
            ToolCandidate(
                f"{mvn} verify", "test", "language_default", "pom.xml", "java_kotlin"
            )
        )
        candidates.append(
            ToolCandidate(
                f"{mvn} package", "build", "language_default", "pom.xml", "java_kotlin"
            )
        )
    if is_gradle:
        gradle = "./gradlew" if tree_has(tree, "gradlew") else "gradle"
        candidates.append(
            ToolCandidate(
                f"{gradle} test",
                "test",
                "language_default",
                "build.gradle",
                "java_kotlin",
            )
        )
        candidates.append(
            ToolCandidate(
                f"{gradle} build",
                "build",
                "language_default",
                "build.gradle",
                "java_kotlin",
            )
        )

    return candidates


def probe_dotnet(root: Path, tree: Set[str]) -> List[ToolCandidate]:
    return [
        ToolCandidate("dotnet test", "test", "language_default", "*.csproj", "dotnet"),
        ToolCandidate(
            "dotnet build", "build", "language_default", "*.csproj", "dotnet"
        ),
        ToolCandidate(
            "dotnet format --verify-no-changes",
            "format",
            "language_default",
            "*.csproj",
            "dotnet",
        ),
    ]


def probe_justfile(root: Path, tree: Set[str]) -> List[ToolCandidate]:
    candidates: List[ToolCandidate] = []
    if not tree_has(tree, "Justfile") and not tree_has(tree, "justfile"):
        return candidates
    just_path = root / "Justfile" if tree_has(tree, "Justfile") else root / "justfile"
    content = read_text(just_path)
    if not content:
        return candidates
    kind_keywords = ["lint", "test", "build", "format", "typecheck", "check"]
    for line in content.split("\n"):
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*):", line)
        if m:
            recipe = m.group(1)
            recipe_lower = recipe.lower()
            for kw in kind_keywords:
                if kw in recipe_lower:
                    kind = "typecheck" if kw == "check" else kw
                    candidates.append(
                        ToolCandidate(
                            f"just {recipe}",
                            kind,
                            "config_file",
                            f"Justfile recipe {recipe}",
                            "unknown",
                        )
                    )
                    break
    return candidates


def probe_makefile(root: Path, tree: Set[str]) -> List[ToolCandidate]:
    candidates: List[ToolCandidate] = []
    if not tree_has(tree, "Makefile") and not tree_has(tree, "makefile"):
        return candidates
    make_path = root / "Makefile" if tree_has(tree, "Makefile") else root / "makefile"
    content = read_text(make_path)
    if not content:
        return candidates
    kind_keywords = ["lint", "test", "build", "format", "typecheck", "check"]
    for line in content.split("\n"):
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*):", line)
        if m:
            target = m.group(1)
            target_lower = target.lower()
            for kw in kind_keywords:
                if kw in target_lower:
                    kind = "typecheck" if kw == "check" else kw
                    candidates.append(
                        ToolCandidate(
                            f"make {target}",
                            kind,
                            "config_file",
                            f"Makefile target {target}",
                            "unknown",
                        )
                    )
                    break
    return candidates


# ---------------------------------------------------------------------------
# Command Selection
# ---------------------------------------------------------------------------


def select_best_commands(
    candidates: List[ToolCandidate],
) -> Dict[str, List[ToolCandidate]]:
    """Group by kind, for each kind pick all at highest (lowest numeric) priority."""
    groups = group_candidates_by_kind(candidates)

    selected: Dict[str, List[ToolCandidate]] = {}
    for kind, group in groups.items():
        min_priority = min(c.priority_num() for c in group)
        selected[kind] = [c for c in group if c.priority_num() == min_priority]
    return selected


def group_candidates_by_kind(
    candidates: List[ToolCandidate],
) -> Dict[str, List[ToolCandidate]]:
    """Group all discovered candidates by command kind."""
    groups: Dict[str, List[ToolCandidate]] = {}
    for c in candidates:
        groups.setdefault(c.kind, []).append(c)
    return groups


# ---------------------------------------------------------------------------
# Additional Scan Discovery
# ---------------------------------------------------------------------------


def discover_additional_scans(
    root: Path, tree: Set[str]
) -> Dict[str, List[Dict[str, Any]]]:
    scans: Dict[str, List[Dict[str, Any]]] = {
        "security": [],
        "boundary": [],
        "duplication": [],
        "dead_code": [],
        "api_contract": [],
        "infra": [],
        "container": [],
        "coverage": [],
    }

    # From package.json
    pkg_content = (
        read_text(root / "package.json") if tree_has(tree, "package.json") else None
    )
    pkg: Dict[str, Any] = {}
    if pkg_content:
        try:
            pkg = json.loads(pkg_content)
        except (json.JSONDecodeError, ValueError):
            pass

    scripts = pkg.get("scripts", {})
    deps = set()
    for dk in ("dependencies", "devDependencies"):
        deps.update(pkg.get(dk, {}).keys())

    # Boundary
    for s in ("check:project-tags", "check:generated-boundaries"):
        if s in scripts:
            scans["boundary"].append(
                ScanCandidate(
                    scripts[s], f"package.json scripts.{s}", s, "boundary"
                ).to_dict()
            )

    # Security
    if "audit" in scripts:
        scans["security"].append(
            ScanCandidate(
                scripts["audit"], "package.json scripts.audit", "audit", "security"
            ).to_dict()
        )
    if "semgrep" in deps:
        scans["security"].append(
            ScanCandidate(
                "semgrep scan", "package.json dependency semgrep", "semgrep", "security"
            ).to_dict()
        )
    for s_name, s_val in scripts.items():
        if "semgrep" in s_name.lower() or "semgrep" in str(s_val).lower():
            scans["security"].append(
                ScanCandidate(
                    s_val, f"package.json scripts.{s_name}", "semgrep", "security"
                ).to_dict()
            )
            break

    # Duplication
    for s_name in scripts:
        if "duplication" in s_name.lower():
            scans["duplication"].append(
                ScanCandidate(
                    scripts[s_name],
                    f"package.json scripts.{s_name}",
                    s_name,
                    "duplication",
                ).to_dict()
            )
    if "jscpd" in deps:
        scans["duplication"].append(
            ScanCandidate(
                "jscpd", "package.json dependency jscpd", "jscpd", "duplication"
            ).to_dict()
        )

    # Dead code
    if "knip" in deps:
        scans["dead_code"].append(
            ScanCandidate(
                "knip", "package.json dependency knip", "knip", "dead_code"
            ).to_dict()
        )
    for s_name in scripts:
        if "knip" in s_name.lower():
            scans["dead_code"].append(
                ScanCandidate(
                    scripts[s_name],
                    f"package.json scripts.{s_name}",
                    "knip",
                    "dead_code",
                ).to_dict()
            )
            break

    # API contract
    for s_name in scripts:
        if "validate:api" in s_name.lower() or "schemathesis" in s_name.lower():
            scans["api_contract"].append(
                ScanCandidate(
                    scripts[s_name],
                    f"package.json scripts.{s_name}",
                    s_name,
                    "api_contract",
                ).to_dict()
            )
    if "schemathesis" in deps:
        scans["api_contract"].append(
            ScanCandidate(
                "schemathesis",
                "package.json dependency schemathesis",
                "schemathesis",
                "api_contract",
            ).to_dict()
        )

    # Infra
    for s_name in scripts:
        if "infra:validate" in s_name.lower():
            scans["infra"].append(
                ScanCandidate(
                    scripts[s_name], f"package.json scripts.{s_name}", s_name, "infra"
                ).to_dict()
            )

    # Container
    for s_name in scripts:
        if "lint:docker" in s_name.lower():
            scans["container"].append(
                ScanCandidate(
                    scripts[s_name],
                    f"package.json scripts.{s_name}",
                    s_name,
                    "container",
                ).to_dict()
            )

    # Coverage
    for s_name in scripts:
        if "coverage" in s_name.lower():
            scans["coverage"].append(
                ScanCandidate(
                    scripts[s_name],
                    f"package.json scripts.{s_name}",
                    s_name,
                    "coverage",
                ).to_dict()
            )

    # From config files
    if tree_has(tree, ".semgrep.yml") or tree_has_dir(tree, ".semgrep"):
        src = ".semgrep.yml" if tree_has(tree, ".semgrep.yml") else ".semgrep/"
        scans["security"].append(
            ScanCandidate("semgrep scan", src, "semgrep", "security").to_dict()
        )
    if tree_has(tree, "bandit.yaml") or tree_has(tree, ".bandit"):
        scans["security"].append(
            ScanCandidate(
                "bandit -r .", "bandit config", "bandit", "security"
            ).to_dict()
        )
    if tree_has(tree, ".spotbugs.xml"):
        scans["security"].append(
            ScanCandidate("spotbugs", ".spotbugs.xml", "spotbugs", "security").to_dict()
        )

    # Dependency audit from config
    if tree_has(tree, ".github/dependabot.yml"):
        scans.setdefault("dependency_audit", []).append(
            ScanCandidate(
                "dependabot", ".github/dependabot.yml", "dependabot", "dependency_audit"
            ).to_dict()
        )
    for reno in ("renovate.json", ".renovate.json", "renovate.json5"):
        if tree_has(tree, reno):
            scans.setdefault("dependency_audit", []).append(
                ScanCandidate(
                    "renovate", reno, "renovate", "dependency_audit"
                ).to_dict()
            )
            break

    # Remove empty categories
    return {k: v for k, v in scans.items() if v}


# ---------------------------------------------------------------------------
# CI Workflow Scanning
# ---------------------------------------------------------------------------


def make_source(file: str, source_type: str, detail: Optional[str] = None) -> Dict[str, str]:
    source = {"file": file, "type": source_type}
    if detail:
        source["detail"] = detail
    return source


def parse_source_reference(source: str, source_type: str) -> Dict[str, str]:
    special_sources = {
        "moon workspace": (".moon/workspace.yml", "workspace"),
        "bandit config": ("bandit.yaml", "config"),
    }
    if source in special_sources:
        file, detail = special_sources[source]
        return make_source(file, source_type, detail)

    source_parts = source.split(" ", 1)
    file = source_parts[0]
    detail = source_parts[1] if len(source_parts) > 1 else None
    return make_source(file, source_type, detail)


def candidate_to_source(candidate: ToolCandidate) -> Dict[str, str]:
    return parse_source_reference(
        candidate.source,
        SOURCE_TYPE_BY_PRIORITY.get(candidate.priority, "detected"),
    )


def scan_to_source(scan: Dict[str, Any], source_type: str = "scan_config") -> Dict[str, str]:
    source = parse_source_reference(scan["source"], source_type)
    if scan.get("label"):
        existing_detail = source.get("detail")
        label_detail = f"label={scan['label']}"
        source["detail"] = (
            f"{existing_detail}; {label_detail}" if existing_detail else label_detail
        )
    return source


def advisory_patterns(text: str) -> List[str]:
    patterns = [
        ("continue-on-error: true", "continue-on-error: true"),
        ("continue_on_error: true", "continue_on_error: true"),
        ("|| true", "|| true"),
        ("--exit-zero", "--exit-zero"),
        ("<failonviolation>false</failonviolation>", "failOnViolation=false"),
        ("<failonviolation>false", "failOnViolation=false"),
        ("allow_failure: true", "allow_failure: true"),
    ]
    return [label for needle, label in patterns if needle in text]


def read_ci_workflows(root: Path, tree: Set[str]) -> List[Dict[str, str]]:
    """Load GitHub Actions and Jenkins workflow files with their paths."""
    workflow_files = [
        p
        for p in tree
        if p.startswith(".github/workflows/")
        and (p.endswith(".yml") or p.endswith(".yaml"))
    ]
    contents: List[Dict[str, str]] = []
    for wf in workflow_files:
        content = read_text(root / wf)
        if content:
            contents.append({"file": wf, "content": content})
    # Also check Jenkinsfile
    for jf in ["Jenkinsfile", "jenkinsfile", "Jenkinsfile.groovy"]:
        if tree_has(tree, jf):
            content = read_text(root / jf)
            if content:
                contents.append({"file": jf, "content": content})
    return contents


def match_ci_sources(
    ci_workflows: List[Dict[str, str]], keywords: List[str]
) -> Dict[str, Any]:
    sources: List[Dict[str, str]] = []
    ci_enforced = False
    advisory_signals: List[str] = []

    for workflow in ci_workflows:
        content_lower = workflow["content"].lower()
        matched_keywords = [kw for kw in keywords if kw in content_lower]
        if not matched_keywords:
            continue

        advisory_hits = advisory_patterns(content_lower)
        detail_parts = [f"keywords={','.join(sorted(set(matched_keywords)))}"]
        if advisory_hits:
            detail_parts.append(f"advisory={','.join(sorted(set(advisory_hits)))}")
            advisory_signals.extend(
                f"{workflow['file']}: {advisory_hit}" for advisory_hit in advisory_hits
            )
        else:
            ci_enforced = True

        sources.append(
            make_source(
                workflow["file"],
                "ci_enforcement",
                "; ".join(detail_parts),
            )
        )

    return {
        "sources": sources,
        "ci_enforced": ci_enforced,
        "advisory_signals": advisory_signals,
    }


# ---------------------------------------------------------------------------
# Category Signal Detection
# ---------------------------------------------------------------------------


def detect_cat1(root: Path, tree: Set[str]) -> Dict[str, Any]:
    """Cat 1: Spec-Driven"""
    signals: Dict[str, Any] = {}
    evidence: List[str] = []

    # Spec directories
    has_openspec = tree_has_dir(tree, "openspec")
    has_specify = tree_has_dir(tree, "specify")
    has_specs = tree_has_dir(tree, "specs")
    signals["openspec_dir"] = has_openspec
    signals["specify_dir"] = has_specify
    signals["specs_dir"] = has_specs
    if has_openspec:
        evidence.append("openspec/ directory found")
    if has_specify:
        evidence.append("specify/ directory found")
    if has_specs:
        evidence.append("specs/ directory found")

    # CLI deps
    pkg_content = (
        read_text(root / "package.json") if tree_has(tree, "package.json") else None
    )
    has_cli_dep = False
    if pkg_content:
        try:
            pkg = json.loads(pkg_content)
            all_deps = set()
            for dk in ("dependencies", "devDependencies"):
                all_deps.update(pkg.get(dk, {}).keys())
            if "@openspec/cli" in all_deps or "specify" in all_deps:
                has_cli_dep = True
                evidence.append("Spec CLI dependency found")
        except (json.JSONDecodeError, ValueError):
            pass
    signals["cli_dep"] = has_cli_dep

    apm_manifest = parse_apm_manifest(root, tree)

    # Workflow skills
    opencode_skills = [
        p for p in tree if p.startswith(".opencode/skills/") and "openspec" in p.lower()
    ]
    apm_workflow_skills = [
        s
        for s in apm_manifest["skills"]
        if "openspec" in s.lower() or "spec" in s.lower()
    ]
    signals["workflow_skills"] = len(opencode_skills) + len(apm_workflow_skills)
    if opencode_skills:
        evidence.append(f"{len(opencode_skills)} openspec workflow skills")
    if apm_workflow_skills:
        evidence.append(
            f"{len(apm_workflow_skills)} remote spec workflow skills in apm.yml"
        )

    # Workflow commands
    opencode_commands = [
        p
        for p in tree
        if p.startswith(".opencode/command/") or p.startswith(".opencode/commands/")
    ]
    signals["workflow_commands"] = len(opencode_commands)
    if opencode_commands:
        evidence.append(f"{len(opencode_commands)} workflow commands")

    # GitHub prompts
    has_prompts = tree_has_dir(tree, ".github/prompts")
    signals["github_prompts"] = has_prompts
    if has_prompts:
        evidence.append(".github/prompts/ found")

    # CONTRIBUTING.md mentions
    contrib_content = (
        read_text(root / "CONTRIBUTING.md")
        if tree_has(tree, "CONTRIBUTING.md")
        else None
    )
    contrib_mentions_spec = False
    if contrib_content:
        lower = contrib_content.lower()
        contrib_mentions_spec = any(w in lower for w in ["spec", "openspec", "specify"])
    signals["contributing_mentions_spec"] = contrib_mentions_spec
    if contrib_mentions_spec:
        evidence.append("CONTRIBUTING.md mentions specs")

    # AGENTS.md mentions
    agents_content = (
        read_text(root / "AGENTS.md") if tree_has(tree, "AGENTS.md") else None
    )
    agents_mentions_spec = False
    if agents_content:
        lower = agents_content.lower()
        agents_mentions_spec = any(w in lower for w in ["spec", "openspec", "specify"])
    signals["agents_mentions_spec"] = agents_mentions_spec
    if agents_mentions_spec:
        evidence.append("AGENTS.md mentions specs")

    # Changes count
    changes = [
        p
        for p in tree
        if p.startswith("openspec/changes/")
        and not p.startswith("openspec/changes/archive/")
    ]
    archived = [p for p in tree if p.startswith("openspec/changes/archive/")]
    signals["changes_count"] = len(changes)
    signals["archived_count"] = len(archived)
    signals["has_openspec_activity"] = bool(changes or archived)
    if changes:
        evidence.append(f"{len(changes)} active changes")
    if archived:
        evidence.append(f"{len(archived)} archived items")

    return {"signals": signals, "evidence": evidence}


def _detect_enforcement_locus(
    kind: str,
    candidates_by_kind: Dict[str, List[ToolCandidate]],
    ci_workflows: List[Dict[str, str]],
    ci_keywords: List[str],
    pkg_scripts: Dict[str, Any],
    tree: Set[str],
) -> Dict[str, Any]:
    """Detect WHERE a check is enforced: local_script, precommit, validate_command, ci.

    Returns a dict with detected, ci_enforced, enforcement metadata, locus list,
    and structured sources.
    """
    detected = kind in candidates_by_kind
    ci_matches = match_ci_sources(ci_workflows, ci_keywords)
    ci_enforced = ci_matches["ci_enforced"]

    sources: List[Dict[str, str]] = []
    locus: List[str] = []
    enforced_anywhere = False
    advisory_signals = list(ci_matches["advisory_signals"])

    if detected:
        sources.extend(candidate_to_source(candidate) for candidate in candidates_by_kind[kind])
        locus.append("local_script")

    # Check if wired into precommit
    has_precommit_config = tree_has(tree, ".pre-commit-config.yaml")
    has_husky = tree_has_dir(tree, ".husky")
    precommit_script_body = pkg_scripts.get("precommit", "")
    if isinstance(precommit_script_body, str) and kind in precommit_script_body.lower():
        locus.append("precommit")
        advisory_hits = advisory_patterns(precommit_script_body.lower())
        detail = f"scripts.precommit ({kind})"
        if advisory_hits:
            advisory_signals.extend(
                f"package.json scripts.precommit: {advisory_hit}"
                for advisory_hit in advisory_hits
            )
            detail = f"{detail}; advisory={','.join(sorted(set(advisory_hits)))}"
        else:
            enforced_anywhere = True
        sources.append(make_source("package.json", "script_entry", detail))
    elif has_husky or has_precommit_config:
        # If hooks exist, the kind is likely wired through them
        if detected:
            locus.append("precommit")
            enforced_anywhere = True
            if has_precommit_config:
                sources.append(make_source(".pre-commit-config.yaml", "hook_config", kind))
            if has_husky:
                sources.append(make_source(".husky/", "hook_config", kind))

    # Check if wired into validate/check command
    for script_name in ("validate", "check"):
        body = pkg_scripts.get(script_name, "")
        if isinstance(body, str) and kind in body.lower():
            locus.append("validate_command")
            advisory_hits = advisory_patterns(body.lower())
            detail = f"scripts.{script_name} ({kind})"
            if advisory_hits:
                advisory_signals.extend(
                    f"package.json scripts.{script_name}: {advisory_hit}"
                    for advisory_hit in advisory_hits
                )
                detail = f"{detail}; advisory={','.join(sorted(set(advisory_hits)))}"
            else:
                enforced_anywhere = True
            sources.append(make_source("package.json", "script_entry", detail))
            break

    if ci_matches["sources"]:
        sources.extend(ci_matches["sources"])
        locus.append("ci")
    if ci_enforced:
        enforced_anywhere = True

    enforcement_mode = "none"
    if advisory_signals and not enforced_anywhere:
        enforcement_mode = "advisory"
    elif enforced_anywhere:
        enforcement_mode = "enforced"

    return {
        "detected": detected,
        "ci_enforced": ci_enforced,
        "enforcement_mode": enforcement_mode,
        "advisory_signals": sorted(set(advisory_signals)),
        "locus": sorted(set(locus)),
        "sources": sources,
    }


def detect_cat2(
    root: Path,
    tree: Set[str],
    candidates_by_kind: Dict[str, List[ToolCandidate]],
    scans: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """Cat 2: Deterministic Checks"""
    ci_workflows = read_ci_workflows(root, tree)
    ci_lower = "\n".join(workflow["content"] for workflow in ci_workflows).lower()

    pkg_content = (
        read_text(root / "package.json") if tree_has(tree, "package.json") else None
    )
    pkg_scripts: Dict[str, Any] = {}
    if pkg_content:
        try:
            pkg_scripts = json.loads(pkg_content).get("scripts", {})
        except (json.JSONDecodeError, ValueError):
            pkg_scripts = {}

    signals: Dict[str, Any] = {}
    evidence: List[str] = []
    # Core checks with enforcement locus tracking
    signals["lint"] = _detect_enforcement_locus(
        "lint",
        candidates_by_kind,
        ci_workflows,
        ["eslint", "ruff", "flake8", "lint", "clippy", "golangci"],
        pkg_scripts,
        tree,
    )
    signals["typecheck"] = _detect_enforcement_locus(
        "typecheck",
        candidates_by_kind,
        ci_workflows,
        ["tsc", "mypy", "pyright", "typecheck", "type-check"],
        pkg_scripts,
        tree,
    )
    signals["test"] = _detect_enforcement_locus(
        "test",
        candidates_by_kind,
        ci_workflows,
        ["test", "pytest", "vitest", "jest", "cargo test", "go test"],
        pkg_scripts,
        tree,
    )
    signals["build"] = _detect_enforcement_locus(
        "build",
        candidates_by_kind,
        ci_workflows,
        ["build", "docker", "cargo build", "dotnet build"],
        pkg_scripts,
        tree,
    )

    # Lint strictness: check for --max-warnings=0 or equivalent
    lint_strict = False
    lint_strict_evidence: List[Dict[str, str]] = []
    # Check package.json lint script for --max-warnings=0
    lint_script_body = pkg_scripts.get("lint", "")
    if (
        isinstance(lint_script_body, str)
        and "--max-warnings" in lint_script_body
        and "=0" in lint_script_body
    ):
        lint_strict = True
        lint_strict_evidence.append(
            make_source("package.json", "script_entry", "scripts.lint; --max-warnings=0")
        )
    # Check CI content for --max-warnings=0
    if "--max-warnings" in ci_lower and "=0" in ci_lower:
        lint_strict = True
        for workflow in ci_workflows:
            workflow_lower = workflow["content"].lower()
            if "--max-warnings" in workflow_lower and "=0" in workflow_lower:
                lint_strict_evidence.append(
                    make_source(
                        workflow["file"],
                        "ci_enforcement",
                        "--max-warnings=0",
                    )
                )
    # Check .eslintrc* or eslint.config.* for error-only (shallow check)
    for eslint_conf in tree_glob(tree, "eslint.config.*") + tree_glob(
        tree, ".eslintrc*"
    ):
        content = read_text(root / eslint_conf)
        if content and "--max-warnings" in content and "0" in content:
            lint_strict = True
            lint_strict_evidence.append(
                make_source(eslint_conf, "config", "references max-warnings 0")
            )
    # Check for biome strict (biome uses "error" severity by default)
    if tree_has(tree, "biome.json") or tree_has(tree, "biome.jsonc"):
        lint_strict = True
        lint_strict_evidence.append(
            make_source(
                "biome.json" if tree_has(tree, "biome.json") else "biome.jsonc",
                "config",
                "error severity by default",
            )
        )
    signals["lint"]["strict"] = lint_strict
    signals["lint"]["strict_evidence"] = lint_strict_evidence

    # Test lanes
    test_lanes: List[str] = []
    for name in pkg_scripts.keys():
        lowered = name.lower()
        if lowered == "test" or lowered.startswith("test:"):
            test_lanes.append(name)
        elif "integration" in lowered or "e2e" in lowered:
            test_lanes.append(name)
    if (
        re.search(r"(:|\b)test:integration\b", ci_lower)
        or "integration tests" in ci_lower
    ):
        test_lanes.append("integration")
    if (
        re.search(r"(:|\b)e2e\b", ci_lower)
        or "playwright" in ci_lower
        or "frontend-e2e" in ci_lower
    ):
        test_lanes.append("e2e")
    for project_file in tree_glob(tree, "**/project.json")[:200]:
        content = read_text(root / project_file)
        if not content:
            continue
        lower = content.lower()
        if '"test:integration"' in lower or '"integration"' in lower:
            test_lanes.append("integration")
        if '"e2e"' in lower:
            test_lanes.append("e2e")
    has_integration_lane = any("integration" in lane.lower() for lane in test_lanes)
    has_e2e_lane = any("e2e" in lane.lower() for lane in test_lanes)
    signals["test"]["lanes"] = sorted(set(test_lanes))
    signals["test"]["has_integration_lane"] = has_integration_lane
    signals["test"]["has_e2e_lane"] = has_e2e_lane

    # Changed-line coverage detection
    coverage_signals: Dict[str, Any] = {
        "detected": False,
        "ci_enforced": False,
        "changed_line": False,
        "sources": [],
        "locus": [],
        "enforcement_mode": "none",
        "advisory_signals": [],
    }
    coverage_scripts = [name for name in pkg_scripts if "coverage" in name.lower()]
    if coverage_scripts:
        coverage_signals["detected"] = True
        coverage_signals["locus"].append("local_script")
        coverage_signals["sources"].extend(
            make_source("package.json", "script_entry", f"scripts.{script_name}")
            for script_name in coverage_scripts
        )
        # Check if it's changed-line coverage (diff-based)
        for cs in coverage_scripts:
            body = pkg_scripts.get(cs, "")
            if isinstance(body, str):
                lower_body = body.lower()
                if any(
                    kw in lower_body
                    for kw in [
                        "--changed",
                        "diff",
                        "new-code",
                        "changed-line",
                        "affected",
                    ]
                ):
                    coverage_signals["changed_line"] = True
                    coverage_signals["sources"].append(
                        make_source(
                            "package.json",
                            "script_entry",
                            f"scripts.{cs}; changed-line coverage",
                        )
                    )
    # Check if coverage:new or similar is in precommit/validate
    precommit_body = pkg_scripts.get("precommit", "")
    if isinstance(precommit_body, str) and "coverage" in precommit_body.lower():
        coverage_signals["locus"].append("precommit")
    for validate_key in ("validate", "check"):
        validate_body = pkg_scripts.get(validate_key, "")
        if isinstance(validate_body, str) and "coverage" in validate_body.lower():
            coverage_signals["locus"].append("validate_command")
            break
    coverage_ci_matches = match_ci_sources(
        ci_workflows, ["coverage", "codecov", "coveralls"]
    )
    if coverage_ci_matches["sources"]:
        coverage_signals["locus"].append("ci")
        coverage_signals["sources"].extend(coverage_ci_matches["sources"])
        coverage_signals["advisory_signals"] = coverage_ci_matches["advisory_signals"]
        if coverage_ci_matches["ci_enforced"]:
            coverage_signals["ci_enforced"] = True
    if coverage_signals["advisory_signals"] and not coverage_signals["ci_enforced"]:
        coverage_signals["enforcement_mode"] = "advisory"
    elif coverage_signals["ci_enforced"] or any(
        coverage_locus in coverage_signals["locus"]
        for coverage_locus in ["precommit", "validate_command"]
    ):
        coverage_signals["enforcement_mode"] = "enforced"
    coverage_signals["locus"] = sorted(set(coverage_signals["locus"]))
    signals["coverage"] = coverage_signals

    # SAST
    sast_detected = bool(scans.get("security"))
    sast_ci_matches = match_ci_sources(
        ci_workflows, ["semgrep", "bandit", "sast", "codeql", "spotbugs"]
    )
    sast_ci = sast_ci_matches["ci_enforced"]
    sast_locus = []
    if sast_detected:
        sast_locus.append("local_script")
    if sast_ci_matches["sources"]:
        sast_locus.append("ci")
    sast_enforcement_mode = "none"
    if sast_ci_matches["advisory_signals"] and not sast_ci:
        sast_enforcement_mode = "advisory"
    elif sast_detected or sast_ci:
        sast_enforcement_mode = "enforced"
    signals["sast"] = {
        "detected": sast_detected,
        "ci_enforced": sast_ci,
        "locus": sast_locus,
        "sources": [scan_to_source(scan) for scan in scans.get("security", [])]
        + sast_ci_matches["sources"],
        "enforcement_mode": sast_enforcement_mode,
        "advisory_signals": sast_ci_matches["advisory_signals"],
    }

    # Dependency audit
    dep_audit_detected = bool(scans.get("dependency_audit"))
    dep_audit_ci_matches = match_ci_sources(
        ci_workflows, ["audit", "dependabot", "renovate", "snyk"]
    )
    dep_audit_ci = dep_audit_ci_matches["ci_enforced"]
    dep_locus = []
    if dep_audit_detected:
        dep_locus.append("local_script")
    if dep_audit_ci_matches["sources"]:
        dep_locus.append("ci")
    # Check for dependabot config file
    if tree_has(tree, ".github/dependabot.yml") or tree_has(
        tree, ".github/dependabot.yaml"
    ):
        if not dep_audit_detected:
            dep_audit_detected = True
        dep_locus.append("config_file")
    # Check for renovate
    if (
        tree_has(tree, "renovate.json")
        or tree_has(tree, ".renovaterc")
        or tree_has(tree, ".renovaterc.json")
    ):
        if not dep_audit_detected:
            dep_audit_detected = True
        dep_locus.append("config_file")
    dep_locus = sorted(set(dep_locus))
    signals["dependency_audit"] = {
        "detected": dep_audit_detected,
        "ci_enforced": dep_audit_ci,
        "locus": dep_locus,
        "sources": [scan_to_source(scan) for scan in scans.get("dependency_audit", [])]
        + dep_audit_ci_matches["sources"],
        "enforcement_mode": (
            "advisory"
            if dep_audit_ci_matches["advisory_signals"] and not dep_audit_ci
            else "enforced"
            if dep_audit_detected or dep_audit_ci
            else "none"
        ),
        "advisory_signals": dep_audit_ci_matches["advisory_signals"],
    }

    # Local validation
    has_precommit = tree_has(tree, ".pre-commit-config.yaml")
    has_husky = tree_has_dir(tree, ".husky")
    has_validate_script = False
    has_precommit_script = False
    if pkg_scripts:
        has_validate_script = any(
            k in pkg_scripts for k in ["validate", "check", "precommit"]
        )
        has_precommit_script = "precommit" in pkg_scripts
    lv_locus = []
    if has_precommit or has_husky:
        lv_locus.append("precommit")
    if has_validate_script:
        lv_locus.append("validate_command")
    signals["local_validation"] = {
        "detected": has_precommit or has_husky or has_validate_script,
        "ci_enforced": False,
        "enforcement_mode": "enforced"
        if has_precommit or has_husky or has_validate_script
        else "none",
        "locus": lv_locus,
        "sources": (
            [make_source(".pre-commit-config.yaml", "hook_config")]
            if has_precommit
            else []
        )
        + ([make_source(".husky/", "hook_config")] if has_husky else [])
        + (
            [make_source("package.json", "script_entry", "scripts.validate/check")]
            if has_validate_script
            else []
        )
        + (
            [make_source("package.json", "script_entry", "scripts.precommit")]
            if has_precommit_script
            else []
        ),
        "advisory_signals": [],
    }

    for key, val in signals.items():
        if val.get("detected"):
            locus_str = ", ".join(val.get("locus", [])) or "detected"
            enforcement_mode = val.get("enforcement_mode")
            ci_str = ""
            if enforcement_mode == "advisory":
                ci_str = " (advisory)"
            elif val.get("ci_enforced"):
                ci_str = " (CI enforced)"
            extra = ""
            if key == "lint" and val.get("strict"):
                extra = " [strict]"
            if key == "coverage" and val.get("changed_line"):
                extra = " [changed-line]"
            evidence.append(f"{key}: {locus_str}{ci_str}{extra}")

    return {"signals": signals, "evidence": evidence}


def detect_cat3(root: Path, tree: Set[str]) -> Dict[str, Any]:
    """Cat 3: AI Skills"""
    signals: Dict[str, Any] = {}
    evidence: List[str] = []

    # Find SKILL.md files (local skills)
    skill_dirs = set()
    skill_paths: Dict[str, str] = {}  # skill_name -> path to SKILL.md
    for prefix in ["skills/", ".opencode/skills/", ".github/skills/"]:
        for p in tree:
            if p.startswith(prefix) and p.endswith("SKILL.md"):
                parts = p.split("/")
                if len(parts) >= 3:
                    name = (
                        parts[1]
                        if prefix == "skills/"
                        else parts[2]
                        if len(parts) > 2
                        else parts[1]
                    )
                    skill_dirs.add(name)
                    skill_paths[name] = p

    # Check apm.yml for skill manifest and remote skill dependencies
    apm_manifest = parse_apm_manifest(root, tree)
    signals["has_apm"] = apm_manifest["present"]
    apm_skills = apm_manifest["skills"]
    apm_security_skills = apm_manifest["security_skills"]
    apm_mcp_count = apm_manifest["mcp_entries"]
    if apm_manifest["present"]:
        evidence.append("apm.yml skill manifest found")

    total_local = len(skill_dirs)
    total_apm = len(apm_skills)
    total_all = total_local + total_apm
    signals["total_skills"] = total_all
    signals["local_skills"] = total_local
    signals["apm_skills"] = total_apm
    signals["apm_mcp_count"] = apm_mcp_count
    if total_all:
        evidence.append(f"{total_all} skills ({total_local} local, {total_apm} apm)")

    # All skills count as workflow skills
    signals["core_workflow_skills"] = total_all

    # Security skills: check local SKILL.md content + apm paths
    security_keywords_content = [
        "security review",
        "security scan",
        "vulnerability",
        "sast",
        "cve",
        "supply chain",
        "threat model",
        "codeguard",
        "security audit",
    ]
    security_skills: List[str] = []
    for name, path in skill_paths.items():
        content = read_text(root / path)
        if content:
            lower = content.lower()
            if any(kw in lower for kw in security_keywords_content):
                security_skills.append(name)
    # Add apm security skills (path-based)
    for dep in apm_security_skills:
        skill_name = dep.split("/")[-1] if "/" in dep else dep
        if skill_name not in security_skills:
            security_skills.append(skill_name)
    signals["security_skills"] = len(security_skills)
    if security_skills:
        evidence.append(f"Security skills: {', '.join(sorted(security_skills))}")

    # Check for skills CLI dep
    pkg_content = (
        read_text(root / "package.json") if tree_has(tree, "package.json") else None
    )
    has_skills_cli = False
    if pkg_content:
        try:
            pkg = json.loads(pkg_content)
            all_deps = set()
            for dk in ("dependencies", "devDependencies"):
                all_deps.update(pkg.get(dk, {}).keys())
            has_skills_cli = any("skills" in d.lower() for d in all_deps)
        except (json.JSONDecodeError, ValueError):
            pass
    signals["skills_cli"] = has_skills_cli

    return {"signals": signals, "evidence": evidence}


def detect_cat4(root: Path, tree: Set[str]) -> Dict[str, Any]:
    """Cat 4: Documentation Tree"""
    signals: Dict[str, Any] = {}
    evidence: List[str] = []

    # AGENTS.md
    agents_exists = tree_has(tree, "AGENTS.md")
    agents_content = read_text(root / "AGENTS.md") if agents_exists else None
    agents_lines = len(agents_content.split("\n")) if agents_content else 0
    agents_has_routing = bool(agents_content and "docs/" in agents_content)
    agents_has_tree = False
    if agents_content:
        # Tree characters
        if any(c in agents_content for c in ["├", "└", "│"]):
            agents_has_tree = True
        # Explicit map language
        elif any(
            phrase in agents_content.lower()
            for phrase in [
                "this file is a map",
                "documentation map",
                "repo map",
                "repository map",
                "codebase map",
                "project map",
            ]
        ):
            agents_has_tree = True
        # Table-of-contents style with 5+ local links
        elif len(re.findall(r"\[.*?\]\(((?!http)[^)]+)\)", agents_content)) >= 5:
            agents_has_tree = True
    signals["agents_md"] = {
        "exists": agents_exists,
        "lines": agents_lines,
        "has_routing": agents_has_routing,
        "has_tree": agents_has_tree,
    }
    if agents_exists:
        evidence.append(f"AGENTS.md: {agents_lines} lines")

    # CONTRIBUTING.md
    contrib_exists = tree_has(tree, "CONTRIBUTING.md")
    contrib_content = read_text(root / "CONTRIBUTING.md") if contrib_exists else None
    contrib_mentions_validation = bool(
        contrib_content
        and any(w in contrib_content.lower() for w in ["validation", "testing"])
    )
    contrib_mentions_docs_tree = bool(
        contrib_content and "docs/" in contrib_content.lower()
    )
    contrib_mentions_specs = bool(
        contrib_content
        and any(w in contrib_content.lower() for w in ["spec", "openspec"])
    )
    signals["contributing"] = {
        "exists": contrib_exists,
        "mentions_validation": contrib_mentions_validation,
        "mentions_docs_tree": contrib_mentions_docs_tree,
        "mentions_specs": contrib_mentions_specs,
    }
    if contrib_exists:
        evidence.append("CONTRIBUTING.md exists")

    # docs/
    docs_exists = tree_has_dir(tree, "docs")
    docs_subdirs: List[str] = []
    if docs_exists:
        for p in tree:
            if p.startswith("docs/") and p.endswith("/") and p.count("/") == 2:
                docs_subdirs.append(p.rstrip("/").split("/")[1])
    signals["docs_structure"] = {
        "exists": docs_exists,
        "subdirs": sorted(set(docs_subdirs)),
        "subdir_count": len(set(docs_subdirs)),
        "has_architecture": "architecture" in docs_subdirs,
        "has_validation": "validation" in docs_subdirs,
        "has_guides": "guides" in docs_subdirs,
        "has_api": "api" in docs_subdirs,
    }
    if docs_exists:
        evidence.append(f"docs/ with {len(set(docs_subdirs))} subdirs")

    # Cross-links
    docs_files = [p for p in tree if p.startswith("docs/") and not p.endswith("/")]
    cross_links = 0
    for df in docs_files[:20]:  # limit reads
        content = read_text(root / df)
        if content and "docs/" in content:
            cross_links += 1
    signals["cross_links"] = cross_links

    return {"signals": signals, "evidence": evidence}


def detect_cat5(root: Path, tree: Set[str]) -> Dict[str, Any]:
    """Cat 5: AI IDE"""
    signals: Dict[str, Any] = {}
    evidence: List[str] = []

    ides: Dict[str, Dict[str, Any]] = {}
    apm_manifest = parse_apm_manifest(root, tree)

    # Cursor
    cursor: Dict[str, Any] = {
        "has_config": False,
        "has_mcp": False,
        "has_ignore": False,
        "has_repo_specific": False,
        "has_multiple_contexts": False,
    }
    if tree_has(tree, ".cursorrules"):
        cursor["has_config"] = True
        content = read_text(root / ".cursorrules")
        if content and len(content) > 200:
            cursor["has_repo_specific"] = True
    if tree_has_dir(tree, ".cursor/rules"):
        cursor["has_config"] = True
        cursor["has_multiple_contexts"] = True
    if tree_has(tree, ".cursor/mcp.json"):
        cursor["has_mcp"] = True
    if any(v for v in cursor.values()):
        ides["cursor"] = cursor
        evidence.append("Cursor configured")

    # Copilot
    copilot: Dict[str, Any] = {
        "has_config": False,
        "has_mcp": False,
        "has_ignore": False,
        "has_repo_specific": False,
        "has_multiple_contexts": False,
    }
    if tree_has(tree, ".github/copilot-instructions.md"):
        copilot["has_config"] = True
        content = read_text(root / ".github/copilot-instructions.md")
        if content and len(content) > 200:
            copilot["has_repo_specific"] = True
    if tree_has(tree, ".copilotignore"):
        copilot["has_ignore"] = True
        copilot["has_config"] = True
    if any(v for v in copilot.values()):
        ides["copilot"] = copilot
        evidence.append("Copilot configured")

    # Windsurf
    windsurf: Dict[str, Any] = {
        "has_config": False,
        "has_mcp": False,
        "has_ignore": False,
        "has_repo_specific": False,
        "has_multiple_contexts": False,
    }
    if tree_has(tree, ".windsurfrules"):
        windsurf["has_config"] = True
        content = read_text(root / ".windsurfrules")
        if content and len(content) > 200:
            windsurf["has_repo_specific"] = True
    if tree_has_dir(tree, ".windsurf/rules"):
        windsurf["has_config"] = True
        windsurf["has_multiple_contexts"] = True
    if any(v for v in windsurf.values()):
        ides["windsurf"] = windsurf
        evidence.append("Windsurf configured")

    # Claude
    claude: Dict[str, Any] = {
        "has_config": False,
        "has_mcp": False,
        "has_ignore": False,
        "has_repo_specific": False,
        "has_multiple_contexts": False,
    }
    if tree_has(tree, "CLAUDE.md"):
        claude["has_config"] = True
        content = read_text(root / "CLAUDE.md")
        if content and len(content) > 200:
            claude["has_repo_specific"] = True
    if tree_has_dir(tree, ".claude/commands"):
        claude["has_config"] = True
        claude["has_multiple_contexts"] = True
    if tree_has(tree, ".claude/mcp.json"):
        claude["has_mcp"] = True
    if any(v for v in claude.values()):
        ides["claude"] = claude
        evidence.append("Claude configured")

    # OpenCode
    opencode: Dict[str, Any] = {
        "has_config": False,
        "has_mcp": False,
        "has_ignore": False,
        "has_repo_specific": False,
        "has_multiple_contexts": False,
        "has_commands": False,
        "has_skills": False,
        "has_apm": False,
    }
    if tree_has_dir(tree, ".opencode"):
        opencode["has_config"] = True
    if tree_has(tree, "opencode.json") or tree_has(tree, "opencode.jsonc"):
        opencode["has_config"] = True
        cfg_file = (
            "opencode.json" if tree_has(tree, "opencode.json") else "opencode.jsonc"
        )
        content = read_text(root / cfg_file)
        if content and (
            '"mcp"' in content or '"plugin"' in content or len(content) > 200
        ):
            opencode["has_repo_specific"] = True
    if tree_has(tree, ".opencode/mcp.json"):
        opencode["has_mcp"] = True
    # Also check opencode.json/opencode.jsonc for "mcp" key
    if not opencode["has_mcp"]:
        for cfg_name in ["opencode.json", "opencode.jsonc"]:
            if tree_has(tree, cfg_name):
                cfg_content = read_text(root / cfg_name)
                if cfg_content and '"mcp"' in cfg_content:
                    opencode["has_mcp"] = True
                    break
    # Multiple contexts from skills
    opencode_skills = [
        p for p in tree if p.startswith(".opencode/skills/") and p.endswith("SKILL.md")
    ]
    opencode_commands = [
        p
        for p in tree
        if p.startswith(".opencode/command/") or p.startswith(".opencode/commands/")
    ]
    if opencode_skills:
        opencode["has_skills"] = True
    if opencode_commands:
        opencode["has_commands"] = True
    if len(opencode_skills) + len(opencode_commands) > 1:
        opencode["has_multiple_contexts"] = True
    if apm_manifest["present"]:
        opencode["has_apm"] = True
        opencode["has_config"] = True
    if apm_manifest["mcp_entries"] > 0:
        opencode["has_mcp"] = True
    if any(v for v in opencode.values()):
        ides["opencode"] = opencode
        evidence.append("OpenCode configured")
        if opencode_commands:
            evidence.append(f"{len(opencode_commands)} OpenCode commands")
        if opencode_skills:
            evidence.append(f"{len(opencode_skills)} OpenCode skills")
        if apm_manifest["present"]:
            evidence.append("apm.yml extends cross-agent OpenCode config")

    signals["ides"] = ides
    signals["ide_count"] = len(ides)

    return {"signals": signals, "evidence": evidence}


def detect_cat6(root: Path, tree: Set[str]) -> Dict[str, Any]:
    """Cat 6: Agentic Legibility — 8 deterministic sub-metrics"""
    signals: Dict[str, Any] = {}
    evidence: List[str] = []

    # 1.1 Static entry points
    has_entry = tree_has(tree, "AGENTS.md") or tree_has(tree, "README.md")
    signals["static_entry_points"] = has_entry
    if has_entry:
        evidence.append("Static entry point (AGENTS.md or README.md)")

    # 4.1 Repo map
    has_repo_map = False
    for f in ["AGENTS.md", "README.md"]:
        if tree_has(tree, f):
            content = read_text(root / f)
            if content:
                # Tree characters
                if any(c in content for c in ["├", "└"]):
                    has_repo_map = True
                    break
                # Explicit map language
                lower = content.lower()
                if any(
                    phrase in lower
                    for phrase in [
                        "this file is a map",
                        "documentation map",
                        "repo map",
                        "repository map",
                        "codebase map",
                        "project map",
                    ]
                ):
                    has_repo_map = True
                    break
                # Table-of-contents style with multiple doc links (3+ markdown links to local paths)
                local_links = re.findall(r"\[.*?\]\(((?!http)[^)]+)\)", content)
                if len(local_links) >= 5:
                    has_repo_map = True
                    break
    signals["repo_map"] = has_repo_map
    if has_repo_map:
        evidence.append("Repo map found")

    # 4.2 Contributing routes to docs
    contrib_routes = False
    if tree_has(tree, "CONTRIBUTING.md"):
        content = read_text(root / "CONTRIBUTING.md")
        if content and (
            "docs/" in content.lower() or re.search(r"\[.*\]\(.*docs", content.lower())
        ):
            contrib_routes = True
    signals["contributing_routes_docs"] = contrib_routes
    if contrib_routes:
        evidence.append("CONTRIBUTING.md routes to docs")

    # 5.1 Validation command discoverable
    validation_discoverable = False
    if tree_has(tree, "package.json"):
        pkg_content = read_text(root / "package.json")
        if pkg_content:
            try:
                scripts = json.loads(pkg_content).get("scripts", {})
                validation_discoverable = any(
                    k in scripts for k in ["validate", "check", "verify"]
                )
            except (json.JSONDecodeError, ValueError):
                pass
    if not validation_discoverable and (
        tree_has(tree, "Makefile") or tree_has(tree, "makefile")
    ):
        make_path = (
            root / "Makefile" if tree_has(tree, "Makefile") else root / "makefile"
        )
        content = read_text(make_path)
        if content:
            validation_discoverable = bool(
                re.search(r"^(check|validate):", content, re.MULTILINE)
            )
    signals["validation_discoverable"] = validation_discoverable
    if validation_discoverable:
        evidence.append("Validation command discoverable")

    # 5.2 Test command discoverable
    signals["test_discoverable"] = False  # Will be set after candidates are known
    # This gets patched later

    # 8.1 CODEOWNERS
    has_codeowners = tree_has(tree, "CODEOWNERS") or tree_has(
        tree, ".github/CODEOWNERS"
    )
    signals["codeowners"] = has_codeowners
    if has_codeowners:
        evidence.append("CODEOWNERS found")

    # 8.2 LICENSE
    has_license = any(
        tree_has(tree, f) for f in ["LICENSE", "LICENSE.md", "LICENCE", "LICENSE.txt"]
    )
    if not has_license and tree_has(tree, "package.json"):
        pkg_content = read_text(root / "package.json")
        if pkg_content:
            try:
                pkg = json.loads(pkg_content)
                has_license = bool(pkg.get("license"))
            except (json.JSONDecodeError, ValueError):
                pass
    signals["license"] = has_license
    if has_license:
        evidence.append(
            "LICENSE found"
            if any(
                tree_has(tree, f)
                for f in ["LICENSE", "LICENSE.md", "LICENCE", "LICENSE.txt"]
            )
            else "package.json license metadata found"
        )

    # 9.1 CHANGELOG or ADR or OpenSpec changes (decision records)
    has_changelog = tree_has(tree, "CHANGELOG.md") or tree_has(tree, "CHANGELOG")
    has_adr = (
        tree_has_dir(tree, "docs/adr")
        or tree_has_dir(tree, "docs/decisions")
        or tree_has_dir(tree, "adr")
    )
    has_openspec_changes = tree_has_dir(tree, "openspec/changes")
    signals["changelog_or_adr"] = has_changelog or has_adr or has_openspec_changes
    if has_changelog:
        evidence.append("CHANGELOG found")
    if has_adr:
        evidence.append("ADR directory found")
    if has_openspec_changes:
        evidence.append("OpenSpec changes (decision records) found")

    return {"signals": signals, "evidence": evidence}


# ---------------------------------------------------------------------------
# Scoring Engine
# ---------------------------------------------------------------------------


def score_cat1(signals: Dict[str, Any]) -> List[Dict[str, Any]]:
    sub_metrics: List[Dict[str, Any]] = []

    # system_and_artifacts
    score = 0
    if signals.get("specs_dir"):
        score = 1
    if signals.get("openspec_dir") or signals.get("specify_dir"):
        score = 2
    if signals.get("cli_dep"):
        score = 3
    if signals.get("changes_count", 0) > 0 and signals.get("archived_count", 0) > 0:
        score = 4
    sub_metrics.append(
        {
            "id": "1.system_and_artifacts",
            "name": "Spec system and artifacts",
            "score": score,
            "max": 4,
        }
    )

    # workflow_commands
    score = 0
    if signals.get("github_prompts"):
        score = 1
    if signals.get("workflow_commands", 0) > 0 or signals.get("workflow_skills", 0) > 0:
        score = max(score, 2)
    if (
        signals.get("workflow_commands", 0) > 0
        and signals.get("workflow_skills", 0) > 0
    ):
        score = 3
    if score == 3 and signals.get("workflow_skills", 0) > 3:
        score = 4
    sub_metrics.append(
        {
            "id": "1.workflow_commands",
            "name": "Workflow commands and skills",
            "score": score,
            "max": 4,
        }
    )

    # documentation
    score = 0
    if signals.get("contributing_mentions_spec") or signals.get("agents_mentions_spec"):
        score = 2
    if signals.get("contributing_mentions_spec") and signals.get(
        "agents_mentions_spec"
    ):
        score = 3
    if (
        score == 3
        and signals.get("openspec_dir")
        and signals.get("has_openspec_activity")
    ):
        score = 4
    sub_metrics.append(
        {
            "id": "1.documentation",
            "name": "Spec documentation",
            "score": score,
            "max": 4,
        }
    )

    return sub_metrics


def score_cat2(signals: Dict[str, Any]) -> List[Dict[str, Any]]:
    sub_metrics: List[Dict[str, Any]] = []
    checks = [
        "lint",
        "typecheck",
        "test",
        "sast",
        "dependency_audit",
        "build",
        "local_validation",
    ]
    for check in checks:
        data = signals.get(check, {})
        detected = data.get("detected", False)
        ci_enforced = data.get("ci_enforced", False)
        locus = data.get("locus", [])
        enforcement_mode = data.get("enforcement_mode", "none")
        enforced_anywhere = (
            enforcement_mode != "advisory"
            and (ci_enforced or "precommit" in locus or "validate_command" in locus)
        )

        score = 0
        strictness_proven = False

        if detected:
            score = 2
        if detected and enforced_anywhere:
            score = 3

        # Score 4 rules per check type
        if score >= 3 and check == "lint":
            if data.get("strict"):
                score = 4
                strictness_proven = True
        elif score >= 3 and check == "test":
            # Multi-lane testing or changed-line coverage = 4
            cov = signals.get("coverage", {})
            if data.get("has_integration_lane") or data.get("has_e2e_lane"):
                score = 4
                strictness_proven = True
            if cov.get("changed_line") and any(
                coverage_locus in cov.get("locus", [])
                for coverage_locus in ["precommit", "validate_command", "ci"]
            ):
                score = 4
                strictness_proven = True
        elif score >= 3 and check not in ("local_validation",):
            # Generic: if enforced in 2+ loci (local_script counts as enforcement locus for
            # checks that are intentionally separate from validate, e.g. SAST)
            enforcement_loci = [
                enforcement_locus
                for enforcement_locus in locus
                if enforcement_locus in ("local_script", "precommit", "validate_command", "ci")
            ]
            if len(enforcement_loci) >= 2:
                score = 4
                strictness_proven = True
        elif check == "local_validation" and detected:
            sources = data.get("sources", [])
            has_hooks = any(
                source.get("file") in [".husky/", ".pre-commit-config.yaml"]
                for source in sources
            )
            has_script = any("script" in source.get("type", "") for source in sources)
            has_precommit = any(
                "precommit" in source.get("detail", "").lower() for source in sources
            )
            if has_hooks and has_script:
                score = 4
                strictness_proven = True
            elif has_hooks or has_script or has_precommit:
                score = 3

        sub_metrics.append(
            {
                "id": f"2.{check}",
                "name": check,
                "score": score,
                "max": 4,
                "capability": detected,
                "strictness_proven": strictness_proven,
                "locus": locus,
            }
        )

    # Add coverage as informational sub-metric (not scored separately, feeds into test)
    cov = signals.get("coverage", {})
    if cov.get("detected"):
        sub_metrics.append(
            {
                "id": "2.coverage",
                "name": "coverage",
                "score": None,  # informational — feeds into test score
                "max": 4,
                "capability": True,
                "changed_line": cov.get("changed_line", False),
                "locus": cov.get("locus", []),
                "note": "Coverage signals feed into test scoring; not scored independently",
            }
        )

    return sub_metrics


def score_cat3(signals: Dict[str, Any]) -> List[Dict[str, Any]]:
    sub_metrics: List[Dict[str, Any]] = []

    # workflow_skills (all skills count)
    total = signals.get("total_skills", 0)
    score = 0
    if total >= 1:
        score = 1
    if total >= 3:
        score = 2
    if total >= 5:
        score = 3
    if total >= 8:
        score = 4
    sub_metrics.append(
        {"id": "3.workflow_skills", "name": "Workflow skills", "score": score, "max": 4}
    )

    # security_skills
    sec = signals.get("security_skills", 0)
    score = 0
    if sec >= 1:
        score = 2
    if sec >= 2:
        score = 3
    if sec >= 3:
        score = 4
    sub_metrics.append(
        {"id": "3.security_skills", "name": "Security skills", "score": score, "max": 4}
    )

    # relevance
    score = 0
    if total > 0:
        score = 2
    if total >= 3:
        score = 3
    if total >= 3 and sec >= 1:
        score = 4
    sub_metrics.append(
        {"id": "3.relevance", "name": "Skill relevance", "score": score, "max": 4}
    )

    return sub_metrics

    return sub_metrics


def score_cat4(signals: Dict[str, Any]) -> List[Dict[str, Any]]:
    sub_metrics: List[Dict[str, Any]] = []

    # agents_md
    am = signals.get("agents_md", {})
    score = 0
    if am.get("exists"):
        score = 1
        if am.get("lines", 0) >= 20:
            score = 2
        if am.get("has_routing"):
            score = 3
        if am.get("has_routing") and am.get("has_tree"):
            score = 4
    sub_metrics.append(
        {"id": "4.agents_md", "name": "AGENTS.md", "score": score, "max": 4}
    )

    # contributing
    c = signals.get("contributing", {})
    score = 0
    if c.get("exists"):
        score = 1
        if c.get("mentions_validation"):
            score = 2
        if c.get("mentions_docs_tree"):
            score = 3
        if (
            c.get("mentions_specs")
            and c.get("mentions_validation")
            and c.get("mentions_docs_tree")
        ):
            score = 4
    sub_metrics.append(
        {"id": "4.contributing", "name": "CONTRIBUTING.md", "score": score, "max": 4}
    )

    # docs_structure
    ds = signals.get("docs_structure", {})
    score = 0
    if ds.get("exists"):
        score = 1
        if ds.get("subdir_count", 0) >= 2:
            score = 2
        if ds.get("subdir_count", 0) >= 4:
            score = 3
        if (
            ds.get("has_architecture")
            and ds.get("has_validation")
            and ds.get("has_guides")
        ):
            score = 4
    sub_metrics.append(
        {"id": "4.docs_structure", "name": "Docs structure", "score": score, "max": 4}
    )

    # content_quality
    cross_links = signals.get("cross_links", 0)
    ds_exists = signals.get("docs_structure", {}).get("exists", False)
    score = 0
    if ds_exists:
        score = 1
        if cross_links >= 2:
            score = 2
        if cross_links >= 5:
            score = 3
        if cross_links >= 10:
            score = 4
    sub_metrics.append(
        {"id": "4.content_quality", "name": "Content quality", "score": score, "max": 4}
    )

    return sub_metrics


def score_cat5(signals: Dict[str, Any]) -> List[Dict[str, Any]]:
    sub_metrics: List[Dict[str, Any]] = []
    ides = signals.get("ides", {})

    # Find best-configured IDE
    best_ide: Optional[Dict[str, Any]] = None
    best_score = -1
    for ide_name, ide_data in ides.items():
        ide_score = sum(1 for v in ide_data.values() if v is True)
        if ide_score > best_score:
            best_score = ide_score
            best_ide = ide_data

    if not best_ide:
        best_ide = {}

    # Compute agent operating surface breadth (distributed config model)
    oc = ides.get("opencode", {})
    surface_signals = [
        oc.get("has_config"),  # opencode.json
        oc.get("has_commands"),  # .opencode/commands/
        oc.get("has_skills"),  # .opencode/skills/
        oc.get("has_apm"),  # apm.yml
        oc.get("has_mcp"),  # MCP servers
    ]
    surface_breadth = sum(1 for s in surface_signals if s)

    # config_exists — evaluates whether the IDE surface is repo-specific
    ide_count = signals.get("ide_count", 0)
    score = 0
    if ide_count >= 1:
        score = 2
    if best_ide.get("has_repo_specific") or surface_breadth >= 3:
        score = 3
    if (
        best_ide.get("has_multiple_contexts")
        or best_ide.get("has_apm")
        or surface_breadth >= 4
    ):
        score = 4
    sub_metrics.append(
        {"id": "5.config_exists", "name": "IDE config exists", "score": score, "max": 4}
    )

    # commands_and_skills — evaluates the agent workflow surface
    score = 0
    if (
        best_ide.get("has_multiple_contexts")
        or oc.get("has_commands")
        or oc.get("has_skills")
    ):
        score = 2
    if oc.get("has_commands") and oc.get("has_skills"):
        score = 3
    if score >= 3 and oc.get("has_apm"):
        score = 4
    elif oc.get("has_apm") and (oc.get("has_commands") or oc.get("has_skills")):
        score = max(score, 3)
        if surface_breadth >= 4:
            score = 4
    sub_metrics.append(
        {
            "id": "5.commands_and_skills",
            "name": "Commands and skills",
            "score": score,
            "max": 4,
        }
    )

    # mcp_integration
    score = 0
    if best_ide.get("has_mcp") or oc.get("has_mcp"):
        score = 3
    if (best_ide.get("has_mcp") or oc.get("has_mcp")) and (
        best_ide.get("has_repo_specific") or surface_breadth >= 3
    ):
        score = 4
    sub_metrics.append(
        {"id": "5.mcp_integration", "name": "MCP integration", "score": score, "max": 4}
    )

    return sub_metrics


def score_cat6(signals: Dict[str, Any]) -> List[Dict[str, Any]]:
    sub_metrics: List[Dict[str, Any]] = []
    deterministic = [
        ("6.static_entry_points", "Static entry points", "static_entry_points"),
        ("6.repo_map", "Repo map", "repo_map"),
        (
            "6.contributing_routes_docs",
            "Contributing routes to docs",
            "contributing_routes_docs",
        ),
        (
            "6.validation_discoverable",
            "Validation command discoverable",
            "validation_discoverable",
        ),
        ("6.test_discoverable", "Test command discoverable", "test_discoverable"),
        ("6.codeowners", "CODEOWNERS", "codeowners"),
        ("6.license", "LICENSE", "license"),
        ("6.changelog_or_adr", "CHANGELOG or ADR", "changelog_or_adr"),
    ]
    for metric_id, name, key in deterministic:
        val = signals.get(key, False)
        score = 4 if val else 0
        sub_metrics.append({"id": metric_id, "name": name, "score": score, "max": 4})

    # 10 N/A sub-metrics (require content reasoning)
    na_metrics = [
        "6.semantic_naming",
        "6.api_docs_quality",
        "6.error_handling_patterns",
        "6.code_comments_quality",
        "6.type_coverage_depth",
        "6.dependency_docs",
        "6.architecture_clarity",
        "6.onboarding_path",
        "6.debug_affordances",
        "6.change_impact_clarity",
    ]
    for metric_id in na_metrics:
        name = metric_id.split(".", 1)[1].replace("_", " ").title()
        sub_metrics.append({"id": metric_id, "name": name, "score": None, "max": 4})

    return sub_metrics


def compute_scores(all_sub_metrics: Dict[int, List[Dict[str, Any]]]) -> Dict[str, Any]:
    category_scores: List[Dict[str, Any]] = []
    cat_means: Dict[int, Optional[float]] = {}

    for cat_num in range(1, 7):
        metrics = all_sub_metrics.get(cat_num, [])
        scored = [m for m in metrics if m["score"] is not None]
        if scored:
            mean = sum(m["score"] for m in scored) / len(scored)
            cat_means[cat_num] = mean
        else:
            cat_means[cat_num] = None
        category_scores.append(
            {
                "category": cat_num,
                "mean": cat_means[cat_num],
                "sub_metric_count": len(metrics),
                "scored_count": len(scored),
            }
        )

    # Weighted composite
    total_weight = 0.0
    weighted_sum = 0.0
    for cat_num, mean in cat_means.items():
        if mean is not None:
            w = CATEGORY_WEIGHTS[cat_num]
            weighted_sum += mean * w
            total_weight += w

    composite = weighted_sum / total_weight if total_weight > 0 else 0.0
    composite = round(composite, 2)

    # Tier
    if composite <= 0.9:
        tier = "Unaware"
    elif composite <= 1.9:
        tier = "Nascent"
    elif composite <= 2.9:
        tier = "Structured"
    elif composite <= 3.5:
        tier = "Established"
    else:
        tier = "Exemplary"

    # Flatten sub_metrics
    flat_sub_metrics: List[Dict[str, Any]] = []
    for cat_num in range(1, 7):
        flat_sub_metrics.extend(all_sub_metrics.get(cat_num, []))

    has_partial_cat6 = any(m["score"] is None for m in all_sub_metrics.get(6, []))

    return {
        "sub_metrics": flat_sub_metrics,
        "categories": category_scores,
        "composite": composite,
        "tier": tier,
        "provisional": has_partial_cat6,
    }


def compute_recommended_actions(
    all_sub_metrics: Dict[int, List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    actions: List[Dict[str, Any]] = []
    cat_num_for_metric: Dict[str, int] = {}
    for cat_num in range(1, 7):
        for m in all_sub_metrics.get(cat_num, []):
            cat_num_for_metric[m["id"]] = cat_num

    for cat_num in range(1, 7):
        weight = CATEGORY_WEIGHTS[cat_num]
        for m in all_sub_metrics.get(cat_num, []):
            if m["score"] is None:
                continue
            if m["score"] < 3:
                impact = (3 - m["score"]) / 4.0 * weight
                actions.append(
                    {
                        "sub_metric_id": m["id"],
                        "name": m["name"],
                        "current_score": m["score"],
                        "target_score": 3,
                        "impact": round(impact, 4),
                        "category": cat_num,
                    }
                )

    actions.sort(key=lambda a: -a["impact"])
    return actions


# ---------------------------------------------------------------------------
# AI Validation
# ---------------------------------------------------------------------------


def build_ai_validation(
    selected: Dict[str, List[ToolCandidate]],
    cat2_signals: Dict[str, Any],
    all_sub_metrics: Optional[Dict[int, List[Dict[str, Any]]]] = None,
) -> Dict[str, Any]:
    ambiguous: List[str] = []
    for kind, candidates in selected.items():
        if len(candidates) > 1:
            ambiguous.append(kind)

    suggestions: List[str] = []
    if all_sub_metrics is not None:
        # Cat 6 N/A sub-metrics
        cat6_na = [m for m in all_sub_metrics.get(6, []) if m["score"] is None]
        if cat6_na:
            suggestions.append(
                "Review 10 Cat 6 deep sub-metrics requiring content reasoning"
            )

    # Contradictory signals
    for check_name, check_data in cat2_signals.items():
        if isinstance(check_data, dict):
            if check_data.get("ci_enforced") and not check_data.get("detected"):
                suggestions.append(
                    f"CI has {check_name} but no local config detected — verify setup"
                )

    evidence_gaps: List[Dict[str, Any]] = []
    if all_sub_metrics is not None:
        # Evidence-missing hints: capability present but strictness not proven
        for m in all_sub_metrics.get(2, []):
            if (
                m.get("capability")
                and not m.get("strictness_proven")
                and (m.get("score") or 0) >= 3
            ):
                evidence_gaps.append(
                    {
                        "sub_metric": m["id"],
                        "capability": True,
                        "strictness_proven": False,
                        "current_score": m["score"],
                        "hint": f"{m['name']} is enforced but strictness not mechanically proven - LLM should verify",
                    }
                )
                suggestions.append(
                    f"Verify {m['name']} strictness (capability present, enforcement proof incomplete)"
                )

    return {
        "ambiguous_commands": ambiguous,
        "review_suggestions": suggestions,
        "evidence_gaps": evidence_gaps,
        "status": "not_run",
        "scoring_enabled": all_sub_metrics is not None,
    }


# ---------------------------------------------------------------------------
# Main Assembly
# ---------------------------------------------------------------------------


def main() -> None:
    args = parse_args()
    root = args.repo_root
    tree = build_tree(root)

    # Detect languages, pkg managers, monorepo
    languages = detect_languages(root, tree)
    pkg_mgrs = detect_package_managers(languages, tree)
    monorepo = detect_monorepo(root, tree)

    # Run probes
    all_candidates: List[ToolCandidate] = []
    if "node" in languages:
        all_candidates.extend(probe_node(root, tree, pkg_mgrs.get("node", "npm")))
    if "python" in languages:
        all_candidates.extend(probe_python(root, tree, pkg_mgrs.get("python", "pip")))
    if "rust" in languages:
        all_candidates.extend(probe_rust(root, tree))
    if "go" in languages:
        all_candidates.extend(probe_go(root, tree))
    if "java_kotlin" in languages:
        all_candidates.extend(probe_java_kotlin(root, tree))
    if "dotnet" in languages:
        all_candidates.extend(probe_dotnet(root, tree))

    # Justfile/Makefile wrappers
    all_candidates.extend(probe_justfile(root, tree))
    all_candidates.extend(probe_makefile(root, tree))

    # Select best commands
    candidates_by_kind = group_candidates_by_kind(all_candidates)
    selected = select_best_commands(all_candidates)

    # Discover additional scans
    additional_scans = discover_additional_scans(root, tree)

    # Detect categories
    cat1 = detect_cat1(root, tree)
    cat2 = detect_cat2(root, tree, candidates_by_kind, additional_scans)
    cat3 = detect_cat3(root, tree)
    cat4 = detect_cat4(root, tree)
    cat5 = detect_cat5(root, tree)
    cat6 = detect_cat6(root, tree)

    # Patch cat6 test_discoverable
    cat6["signals"]["test_discoverable"] = "test" in candidates_by_kind

    all_sub_metrics: Optional[Dict[int, List[Dict[str, Any]]]] = None
    scores: Optional[Dict[str, Any]] = None
    recommended_actions: Optional[List[Dict[str, Any]]] = None
    if args.with_scoring:
        all_sub_metrics = {
            1: score_cat1(cat1["signals"]),
            2: score_cat2(cat2["signals"]),
            3: score_cat3(cat3["signals"]),
            4: score_cat4(cat4["signals"]),
            5: score_cat5(cat5["signals"]),
            6: score_cat6(cat6["signals"]),
        }
        scores = compute_scores(all_sub_metrics)
        recommended_actions = compute_recommended_actions(all_sub_metrics)

    ai_validation = build_ai_validation(selected, cat2["signals"], all_sub_metrics)

    # Build candidates output
    commands_output: Dict[str, List[Dict[str, Any]]] = {}
    for c in all_candidates:
        commands_output.setdefault(c.kind, []).append(c.to_dict())

    selected_output: Dict[str, List[Dict[str, Any]]] = {}
    for kind, cands in selected.items():
        if cands:
            selected_output[kind] = [candidate.to_dict() for candidate in cands]

    # Additional scans flat list for top-level
    additional_scans_flat: List[Dict[str, Any]] = []
    for kind, scan_list in additional_scans.items():
        for s in scan_list:
            additional_scans_flat.append(s)

    # Assemble output
    output = {
        "version": VERSION,
        "repo_root": str(root),
        "scoring_enabled": args.with_scoring,
        "languages": languages,
        "package_managers": pkg_mgrs,
        "monorepo": monorepo,
        "candidates": {
            "commands": commands_output,
            "additional_scans": additional_scans,
        },
        "selected_commands": selected_output,
        "additional_scans": additional_scans_flat,
        "categories": {
            "1": {"signals": cat1["signals"], "evidence": cat1["evidence"]},
            "2": {"signals": cat2["signals"], "evidence": cat2["evidence"]},
            "3": {"signals": cat3["signals"], "evidence": cat3["evidence"]},
            "4": {"signals": cat4["signals"], "evidence": cat4["evidence"]},
            "5": {"signals": cat5["signals"], "evidence": cat5["evidence"]},
            "6": {"signals": cat6["signals"], "evidence": cat6["evidence"]},
        },
        "ai_validation": ai_validation,
    }

    if scores is not None:
        output["scores"] = scores
    if recommended_actions is not None:
        output["recommended_actions"] = recommended_actions

    json.dump(output, sys.stdout, indent=2, sort_keys=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
