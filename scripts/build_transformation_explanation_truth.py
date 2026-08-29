#!/usr/bin/env python3
"""Build validation-only semantic transformations with auditable provenance.

The benchmark supplies two kinds of truth that natural clone pairs do not:
correspondence under consistent alpha-renaming, and known irrelevant nodes from
a deterministic dead-code insertion.  Every retained original and transform is
compiled in isolation; transformed test data is never used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
BASELINE_ROOT = ROOT.parent / "CodeGraph4CCDetector"
DEFAULT_SOURCE_ROOT = BASELINE_ROOT
DEFAULT_VALIDATION_MANIFEST = (
    ROOT / "artifacts" / "pilots" / "C1_semantic_optimal_subgraph_pair_seed42"
    / "validation_explanation_manifest.txt"
)
DEFAULT_OUTPUT = ROOT / "external_data" / "explanation_truth" / "gcj_transformations"
JAVA_IDENTIFIER = re.compile(r"\b[A-Za-z_$][A-Za-z0-9_$]*\b")
TYPE = r"(?:byte|short|int|long|float|double|boolean|char|String|[A-Z][A-Za-z0-9_$]*)"
DECLARATION = re.compile(
    r"\b" + TYPE
    + r"(?:\s*<[^;={}()]+>)?(?:\s*\[\s*\])*\s+"
    + r"([A-Za-z_$][A-Za-z0-9_$]*)"
)
RESERVED = {
    "main", "serialVersionUID", "System", "String", "Math", "Arrays",
    "Collections", "Objects", "Class", "Main",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument(
        "--validation-manifest", type=Path, default=DEFAULT_VALIDATION_MANIFEST
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--samples", type=int, default=30)
    parser.add_argument(
        "--javac", type=Path,
        default=ROOT.parent / ".conda" / "codegraph4cc" / "bin" / "javac",
    )
    parser.add_argument("--compile-timeout", type=int, default=30)
    parser.add_argument(
        "--benchmark-name",
        default="validation-only transformation explanation truth",
    )
    return parser.parse_args()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def code_mask(source: str) -> str:
    """Replace comments and literals with spaces while preserving offsets."""
    output = list(source)
    state = "code"
    index = 0
    while index < len(source):
        char = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""
        if state == "code":
            if char == "/" and following == "/":
                output[index] = output[index + 1] = " "
                state = "line_comment"
                index += 2
                continue
            if char == "/" and following == "*":
                output[index] = output[index + 1] = " "
                state = "block_comment"
                index += 2
                continue
            if char == '"':
                output[index] = " "
                state = "string"
            elif char == "'":
                output[index] = " "
                state = "char"
        elif state == "line_comment":
            if char == "\n":
                state = "code"
            else:
                output[index] = " "
        elif state == "block_comment":
            if char == "*" and following == "/":
                output[index] = output[index + 1] = " "
                state = "code"
                index += 2
                continue
            if char != "\n":
                output[index] = " "
        elif state in {"string", "char"}:
            delimiter = '"' if state == "string" else "'"
            if char == "\\":
                output[index] = " "
                if index + 1 < len(source):
                    if source[index + 1] != "\n":
                        output[index + 1] = " "
                    index += 2
                    continue
            if char == delimiter:
                output[index] = " "
                state = "code"
            elif char != "\n":
                output[index] = " "
        index += 1
    return "".join(output)


def declared_identifiers(source: str) -> List[str]:
    masked = code_mask(source)
    candidates = {
        match.group(1) for match in DECLARATION.finditer(masked)
        if match.group(1) not in RESERVED
    }
    # Rank independently of source traversal so the same input always receives
    # the same mapping even if regex implementation details are refactored.
    return sorted(
        candidates,
        key=lambda name: (hashlib.sha256(name.encode("utf-8")).hexdigest(), name),
    )


def replace_code_identifiers(source: str, mapping: Dict[str, str]) -> str:
    masked = code_mask(source)
    pieces = []
    previous = 0
    for match in JAVA_IDENTIFIER.finditer(masked):
        replacement = mapping.get(match.group(0))
        if replacement is None:
            continue
        pieces.extend((source[previous:match.start()], replacement))
        previous = match.end()
    pieces.append(source[previous:])
    return "".join(pieces)


def alpha_rename(source: str) -> Tuple[str, Dict[str, str]]:
    identifiers = declared_identifiers(source)
    all_tokens = set(JAVA_IDENTIFIER.findall(code_mask(source)))
    mapping: Dict[str, str] = {}
    next_index = 0
    for identifier in identifiers:
        while True:
            candidate = "xaiAlpha{:03d}".format(next_index)
            next_index += 1
            if candidate not in all_tokens:
                break
        mapping[identifier] = candidate
        all_tokens.add(candidate)
    return replace_code_identifiers(source, mapping), mapping


def insert_dead_code(source: str) -> Tuple[str, str]:
    masked = code_mask(source)
    main = re.search(
        r"\bpublic\s+static\s+void\s+main\s*\([^)]*\)"
        r"(?:\s+throws\s+[^\{]+)?\s*\{",
        masked,
    )
    if main is None:
        raise ValueError("no public static void main body")
    marker_index = 0
    while "__xai_dead_{:03d}".format(marker_index) in masked:
        marker_index += 1
    marker = "__xai_dead_{:03d}".format(marker_index)
    insertion = (
        "\n        int {0} = 0;\n"
        "        if ({0} != 0) {{ System.out.print(\"\"); }}\n"
    ).format(marker)
    position = main.end()
    return source[:position] + insertion + source[position:], marker


def public_class_name(source: str) -> str:
    masked = code_mask(source)
    match = re.search(
        r"\bpublic\s+(?:(?:final|abstract|strictfp)\s+)*class\s+"
        r"([A-Za-z_$][A-Za-z0-9_$]*)",
        masked,
    )
    return match.group(1) if match else "Submission"


def compile_source(source: str, javac: Path, timeout: int) -> Dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="codeclone_truth_compile_") as temporary:
        directory = Path(temporary)
        source_path = directory / (public_class_name(source) + ".java")
        source_path.write_text(source, encoding="utf-8")
        try:
            completed = subprocess.run(
                [str(javac), "-encoding", "UTF-8", "-d", str(directory), str(source_path)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=timeout, check=False,
            )
            return {
                "success": completed.returncode == 0,
                "returncode": completed.returncode,
                "stderr_tail": completed.stderr[-2000:],
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "returncode": None, "stderr_tail": "timeout"}


def candidate_paths(manifest: Path, source_root: Path) -> Iterable[Tuple[str, Path]]:
    names = {
        name
        for line in manifest.read_text(encoding="utf-8").splitlines()
        for name in line.split()[:2]
    }
    for name in sorted(
        names, key=lambda value: hashlib.sha256(value.encode("utf-8")).hexdigest()
    ):
        yield name, source_root / name


def main() -> int:
    args = parse_args()
    if args.samples <= 0:
        raise ValueError("--samples must be positive")
    if not args.javac.is_file():
        raise FileNotFoundError(str(args.javac))
    source_output = args.output_dir / "sources"
    if args.output_dir.exists():
        shutil.rmtree(args.output_dir)
    source_output.mkdir(parents=True)
    records: List[Dict[str, object]] = []
    rejected: List[Dict[str, object]] = []

    for source_name, source_path in candidate_paths(
            args.validation_manifest, args.source_root):
        if len(records) >= args.samples:
            break
        original = source_path.read_text(encoding="utf-8", errors="replace")
        alpha, mapping = alpha_rename(original)
        if len(mapping) < 2:
            rejected.append({"source": source_name, "reason": "fewer_than_two_identifiers"})
            continue
        try:
            alpha_dead, marker = insert_dead_code(alpha)
        except ValueError as error:
            rejected.append({"source": source_name, "reason": str(error)})
            continue
        compilation = {
            "original": compile_source(original, args.javac, args.compile_timeout),
            "alpha": compile_source(alpha, args.javac, args.compile_timeout),
            "alpha_dead": compile_source(alpha_dead, args.javac, args.compile_timeout),
        }
        if not all(result["success"] for result in compilation.values()):
            rejected.append({
                "source": source_name,
                "reason": "compile_failure",
                "compilation": compilation,
            })
            continue

        identifier = "g{:03d}_{}".format(
            len(records), hashlib.sha256(source_name.encode("utf-8")).hexdigest()[:10]
        )
        names = {
            "original": identifier + "__original.java",
            "alpha": identifier + "__alpha.java",
            "alpha_dead": identifier + "__alpha_dead.java",
        }
        contents = {"original": original, "alpha": alpha, "alpha_dead": alpha_dead}
        for variant, filename in names.items():
            (source_output / filename).write_text(contents[variant], encoding="utf-8")
        records.append({
            "sample_id": identifier,
            "validation_source": source_name,
            "validation_source_sha256": sha256_bytes(original.encode("utf-8")),
            "files": names,
            "file_sha256": {
                variant: sha256_bytes(content.encode("utf-8"))
                for variant, content in contents.items()
            },
            "alpha_mapping": mapping,
            "dead_identifier": marker,
            "compilation": compilation,
            "truth": {
                "original_to_alpha": "semantic_equivalence_and_node_correspondence",
                "alpha_to_alpha_dead": "semantic_equivalence_with_known_irrelevant_nodes",
            },
        })

    if len(records) < args.samples:
        raise RuntimeError(
            "only {} of {} requested transformations passed compilation".format(
                len(records), args.samples
            )
        )
    manifest_sha = sha256_bytes(args.validation_manifest.read_bytes())
    report = {
        "benchmark": args.benchmark_name,
        "samples": len(records),
        "variants_per_sample": ["original", "alpha", "alpha_dead"],
        "semantic_oracle": (
            "consistent identifier alpha-renaming plus an unreachable-at-runtime "
            "zero-valued guarded empty print"
        ),
        "verification": "all original and transformed programs compile in isolation",
        "validation_manifest": str(args.validation_manifest.resolve()),
        "validation_manifest_sha256": manifest_sha,
        "test_used": False,
        "records": records,
        "rejected_candidates": rejected,
    }
    report_path = args.output_dir / "transformation_manifest.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "report": str(report_path),
        "samples": len(records),
        "rejected": len(rejected),
        "generated_java_files": len(records) * 3,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
