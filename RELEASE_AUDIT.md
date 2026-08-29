# Release audit

Audit date: 2026-08-29

## Scope

This repository is the standalone artifact for the graph-pair explanation
paper. It contains `C*` explanation experiments, transformation truth,
per-pair evidence, shared detector reproduction patches, statistical analyses,
and explanation tests. It does not contain continual-learning implementations,
GCJ `B*` or CodeNet `E*` experiment configurations, questionnaires, reviewer
responses, or private review metadata.

The CodeNet studies have one explicit model-file dependency on the separately
released continual-learning repository. That dependency is documented by path
and SHA-256; no continual-learning source code is copied into this repository.

## Verification record

- 24 inherited experiment/protocol configurations validated;
- 17 unit and protocol tests passed in the reference environment;
- 260 JSON files parsed successfully;
- 58 JSONL files with 7,415 records parsed successfully;
- optimal-subgraph, natural-baseline, stochastic-seed, objective-ablation,
  transformation-truth, and runtime statistics recomputed;
- no checkpoint, private key, symlink, or file larger than 90 MB included;
- no local host path or private review material detected;
- no continual-learning implementation detected.

Run `bash tools/verify_release.sh --full` to repeat the automated checks.
Exact curated-artifact and truth-bundle hashes are recorded in
`ARTIFACT_SHA256SUMS`.
