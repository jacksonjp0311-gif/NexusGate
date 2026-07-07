from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "nexus.gitnexus_bridge.v0.1.0"

EXCLUDE_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "env", "__pycache__",
    "node_modules", ".next", "dist", "build", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", ".gitnexus",
}

CODE_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".ps1", ".psm1",
    ".json", ".toml", ".yaml", ".yml", ".md", ".html", ".css",
}

SYMBOL_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".ps1", ".psm1"}
MAX_FILE_BYTES = 900_000


@dataclass
class Symbol:
    name: str
    kind: str
    file: str
    line: int


@dataclass
class Edge:
    source: str
    target: str
    kind: str
    evidence: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def safe_read(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def should_skip(path: Path) -> bool:
    return bool(set(path.parts).intersection(EXCLUDE_DIRS))


def iter_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path):
            continue
        if path.suffix.lower() not in CODE_EXTS:
            continue
        out.append(path)
    return sorted(out, key=lambda p: p.as_posix().lower())


def module_keys_for(root: Path, path: Path) -> set[str]:
    r = rel(root, path)
    no_suffix = r[: -len(path.suffix)] if path.suffix else r
    dotted = no_suffix.replace("/", ".").replace("\\", ".")
    keys = {path.stem, no_suffix, dotted}
    if path.name == "__init__.py":
        keys.add(Path(no_suffix).parent.as_posix().replace("/", "."))
    return {k.strip(".") for k in keys if k.strip(".")}


def extract_python(root: Path, path: Path, text: str) -> tuple[list[Symbol], list[str]]:
    symbols: list[Symbol] = []
    imports: list[str] = []
    try:
        tree = ast.parse(text)
    except Exception:
        return symbols, imports

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            symbols.append(Symbol(node.name, "class", rel(root, path), getattr(node, "lineno", 1)))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append(Symbol(node.name, "function", rel(root, path), getattr(node, "lineno", 1)))
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    imports.append(alias.name)
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module:
                imports.append(module)
            for alias in node.names:
                if module and alias.name:
                    imports.append(module + "." + alias.name)
    return symbols, imports


def extract_js_like(root: Path, path: Path, text: str) -> tuple[list[Symbol], list[str]]:
    symbols: list[Symbol] = []
    imports: list[str] = []

    for pattern in [
        r"from\s+['\"]([^'\"]+)['\"]",
        r"import\s+['\"]([^'\"]+)['\"]",
        r"require\(\s*['\"]([^'\"]+)['\"]\s*\)",
        r"import\(\s*['\"]([^'\"]+)['\"]\s*\)",
    ]:
        imports.extend(match.group(1) for match in re.finditer(pattern, text))

    for kind, pattern in [
        ("class", r"\bclass\s+([A-Za-z_$][A-Za-z0-9_$]*)"),
        ("function", r"\bfunction\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\("),
        ("function", r"\bconst\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(?:async\s*)?\("),
        ("function", r"\bexport\s+function\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\("),
    ]:
        for match in re.finditer(pattern, text):
            line = text[: match.start()].count("\n") + 1
            symbols.append(Symbol(match.group(1), kind, rel(root, path), line))

    return symbols, imports


def extract_powershell(root: Path, path: Path, text: str) -> tuple[list[Symbol], list[str]]:
    symbols: list[Symbol] = []
    imports: list[str] = []
    for match in re.finditer(r"(?im)^\s*function\s+([A-Za-z0-9_\-:]+)", text):
        line = text[: match.start()].count("\n") + 1
        symbols.append(Symbol(match.group(1), "function", rel(root, path), line))
    for match in re.finditer(r"(?im)^\s*(?:Import-Module|\. )\s+['\"]?([^'\"\r\n]+)", text):
        imports.append(match.group(1).strip())
    return symbols, imports


def extract_symbols_and_imports(root: Path, path: Path, text: str) -> tuple[list[Symbol], list[str]]:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return extract_python(root, path, text)
    if suffix in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
        return extract_js_like(root, path, text)
    if suffix in {".ps1", ".psm1"}:
        return extract_powershell(root, path, text)
    return [], []


def resolve_import(root: Path, importer: Path, import_name: str, key_to_file: dict[str, str]) -> str | None:
    cleaned = import_name.strip()
    if not cleaned:
        return None
    if cleaned in key_to_file:
        return key_to_file[cleaned]
    base = cleaned.split(".")[0]
    if base in key_to_file:
        return key_to_file[base]

    if cleaned.startswith("."):
        joined = (importer.parent / cleaned).resolve()
        try:
            rel_joined = joined.relative_to(root.resolve()).as_posix()
        except Exception:
            return None
        for candidate in [
            rel_joined,
            rel_joined + ".js",
            rel_joined + ".ts",
            rel_joined + ".tsx",
            rel_joined + ".jsx",
            rel_joined + ".py",
            rel_joined + "/index.js",
            rel_joined + "/index.ts",
            rel_joined + "/__init__.py",
        ]:
            if candidate in key_to_file.values():
                return candidate

    normalized = cleaned.replace("\\", "/")
    for candidate in key_to_file.values():
        if candidate.endswith(normalized):
            return candidate
        for ext in [".py", ".js", ".ts", ".tsx", ".jsx"]:
            if candidate.endswith(normalized + ext):
                return candidate
    return None


def git_changed_files(root: Path) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(root),
            text=True,
            capture_output=True,
            timeout=12,
            check=False,
        )
    except Exception:
        return []

    changed: list[str] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        path = path.replace("\\", "/")
        if path:
            changed.append(path)
    return sorted(set(changed))


def bounded_blast_radius(changed: list[str], reverse_edges: dict[str, set[str]], max_depth: int = 3) -> dict[str, Any]:
    affected: set[str] = set()
    frontier: deque[tuple[str, int]] = deque((item, 0) for item in changed)
    seen: set[str] = set(changed)

    while frontier:
        node, depth = frontier.popleft()
        if depth >= max_depth:
            continue
        for parent in sorted(reverse_edges.get(node, set())):
            if parent in seen:
                continue
            seen.add(parent)
            affected.add(parent)
            frontier.append((parent, depth + 1))

    score = min(1.0, (len(changed) * 0.08) + (len(affected) * 0.04))
    risk = "high" if score >= 0.75 else "medium" if score >= 0.35 else "low"
    return {
        "changed_files": changed,
        "affected_files": sorted(affected),
        "affected_count": len(affected),
        "risk_score": round(score, 4),
        "risk": risk,
        "max_depth": max_depth,
    }


def build_recommendation(impact: dict[str, Any], edge_count: int, symbol_count: int) -> dict[str, Any]:
    risk = impact.get("risk", "low")
    changed_count = len(impact.get("changed_files", []))
    affected_count = int(impact.get("affected_count", 0))

    if changed_count == 0:
        summary = "No git working-tree changes detected. Run scan to baseline the repo graph."
        action = "baseline"
    elif risk == "high":
        summary = "High codegraph impact pressure. Inspect affected files before durable mutation."
        action = "inspect_before_commit"
    elif risk == "medium":
        summary = "Medium codegraph impact pressure. Review affected files and run compiler/tests."
        action = "review_and_validate"
    else:
        summary = "Low codegraph impact pressure. Continue through normal NexusGate validation."
        action = "normal_validation"

    return {
        "summary": summary,
        "next_action": action,
        "risk": risk,
        "changed_count": changed_count,
        "affected_count": affected_count,
        "edge_count": edge_count,
        "symbol_count": symbol_count,
    }


def compile_graph(root: Path) -> dict[str, Any]:
    files = iter_files(root)
    file_records: dict[str, dict[str, Any]] = {}
    symbols: list[Symbol] = []
    imports_by_file: dict[str, list[str]] = {}
    key_to_file: dict[str, str] = {}

    for path in files:
        r = rel(root, path)
        text = safe_read(path)
        file_records[r] = {
            "path": r,
            "suffix": path.suffix.lower(),
            "bytes": path.stat().st_size,
            "sha256": sha_text(text) if text else "",
        }
        for key in module_keys_for(root, path):
            key_to_file[key] = r

    for path in files:
        r = rel(root, path)
        text = safe_read(path)
        if path.suffix.lower() not in SYMBOL_EXTS:
            imports_by_file[r] = []
            continue
        found_symbols, imports = extract_symbols_and_imports(root, path, text)
        symbols.extend(found_symbols)
        imports_by_file[r] = sorted(set(imports))

    edges: list[Edge] = []
    reverse: dict[str, set[str]] = defaultdict(set)
    path_by_rel = {rel(root, path): path for path in files}

    for source, imports in imports_by_file.items():
        importer_path = path_by_rel.get(source)
        if not importer_path:
            continue
        for item in imports:
            target = resolve_import(root, importer_path, item, key_to_file)
            if not target or target == source:
                continue
            edges.append(Edge(source=source, target=target, kind="imports", evidence=item))
            reverse[target].add(source)

    changed = git_changed_files(root)
    impact = bounded_blast_radius(changed, reverse)
    top_imported = sorted(
        ((target, len(sources)) for target, sources in reverse.items()),
        key=lambda x: x[1],
        reverse=True,
    )[:20]

    packet: dict[str, Any] = {
        "version": VERSION,
        "generated_at": utc_now(),
        "root": str(root),
        "boundary": {
            "evidence_only": True,
            "autonomous_authority": False,
            "shell_execution": False,
            "file_mutation_from_model_output": False,
            "nexus_cell_policy_change": False,
        },
        "counts": {
            "files": len(file_records),
            "symbols": len(symbols),
            "edges": len(edges),
            "changed_files": len(changed),
        },
        "files": file_records,
        "symbols": [asdict(item) for item in symbols],
        "edges": [asdict(item) for item in edges],
        "imports_by_file": imports_by_file,
        "impact": impact,
        "top_imported_files": [{"file": file, "importer_count": count} for file, count in top_imported],
    }
    packet["recommendation"] = build_recommendation(impact, len(edges), len(symbols))
    return packet


def write_outputs(root: Path, packet: dict[str, Any]) -> None:
    for path in [
        root / "reports" / "gitnexus_report_latest.json",
        root / "GITNEXUS" / "reports" / "gitnexus_report_latest.json",
        root / "state" / "gitnexus" / "gitnexus_graph_latest.json",
        root / "GITNEXUS" / "state" / "gitnexus_graph_latest.json",
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")

    manifest = {
        "name": "NexusGate GITNEXUS",
        "version": "v0.1.0",
        "status": "python_native_codegraph_evidence_organ",
        "latest_report": "reports/gitnexus_report_latest.json",
        "boundary": packet["boundary"],
        "counts": packet["counts"],
        "last_generated_at": packet["generated_at"],
    }
    for path in [
        root / "state" / "gitnexus" / "gitnexus_manifest.v0.1.0.json",
        root / "GITNEXUS" / "state" / "gitnexus_manifest.v0.1.0.json",
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    receipt = {
        "ts": utc_now(),
        "event": "gitnexus_scan",
        "version": VERSION,
        "report_sha256": sha_text(json.dumps(packet, sort_keys=True)),
        "counts": packet["counts"],
        "risk": packet["impact"]["risk"],
        "authority": "evidence_only",
    }
    for path in [
        root / "ledger" / "gitnexus" / "gitnexus_ledger.jsonl",
        root / "GITNEXUS" / "ledger" / "gitnexus_ledger.jsonl",
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(receipt, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile NexusGate-native GITNEXUS evidence packet.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    parser.add_argument("--no-write", action="store_true", help="Compile without writing report/ledger files")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    packet = compile_graph(root)

    if not args.no_write:
        write_outputs(root, packet)

    summary = {
        "version": packet["version"],
        "counts": packet["counts"],
        "impact": packet["impact"],
        "recommendation": packet["recommendation"],
        "boundary": packet["boundary"],
    }
    print(json.dumps(summary if args.json else packet["recommendation"], indent=2))
    return 0
