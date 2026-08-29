# TC-SOSP: Semantic Code-Clone Graph-Pair Explanation

This repository contains the source code, frozen configurations,
transformation-based explanation truth, per-pair records, and statistical
analyses for task-conditioned semantic optimal subgraph-pair explanation
(TC-SOSP).

## Contents

| Path | Contents |
|---|---|
| `scripts/` | explanation methods, truth construction, evaluation, and statistics |
| `configs/experiments/C*.json` | natural, truth, robustness, and ablation studies |
| `external_data/explanation_truth/` | exact GCJ and CodeNet transformation bundles |
| `artifacts/pilots/C*/` | natural-pair and robustness per-pair records |
| `artifacts/explanation_truth/C*/` | transformation and negative-pair records |
| `artifacts/comparisons/C*.json` | paired tests, corrections, and runtime reports |
| `patches/` | patches and additions for the pinned upstream repositories |
| `tests/` | subgraph-pair, transformation, negative-pair, and protocol tests |

Continual-learning experiment implementations and reviewer-study materials are
not included. The one CodeNet predictor produced by the continual study is an
explicit external checkpoint dependency described below.

## Quick start

```bash
bash tools/bootstrap_upstream.sh
bash ../CodeGraph4CCDetector/scripts/setup_environment.sh

export CODEGRAPH_ENV_PREFIX="$(cd .. && pwd)/.conda/codegraph4cc"
export PYTHON="$CODEGRAPH_ENV_PREFIX/bin/python"
export LD_LIBRARY_PATH="$CODEGRAPH_ENV_PREFIX/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

"$PYTHON" scripts/validate_configs.py
"$PYTHON" research_cli.py \
  --config configs/experiments/C9_natural_validation_strong_baselines.json \
  --device cuda:0 --dry-run
bash tools/verify_release.sh --full
```

## Predictor checkpoints

The main GCJ studies use the frozen detector checkpoint
`../CodeGraph4CCDetector/artifacts/formal_paper_protocol_seed1337/epoch_013.pt`
with SHA-256
`380bd98d949b428711e66f9e8aa92e1c4ed6d39dcb905e7e0542f34719fca61c`.
It is reproduced with the patched upstream batched runner.

The CodeNet truth studies C10 and C15 use the Paper 1 fragment-replay
checkpoint with SHA-256
`9770ee9b9d0b4fc46a7d0fd4f0d0448430c5fe5afccfd44a55f54ee340bc1678`.
The default configuration expects a sibling checkout named
`Continual-Code-Clone-Detection`; run its E0/E6 seed-42 sequence or place the
verified checkpoint at the configured path. The checkpoint itself is not
duplicated in either Git repository.

## Main studies

- C9: 100 natural GCJ validation graph pairs, balanced by predicted class;
- C8/C10: 30 GCJ and 30 CodeNet programs with identifier-renaming and known
  irrelevant guarded-block truth;
- C15: 15 CodeNet negative graph pairs with bilateral transformation truth;
- C2/C3: 10%, 20%, and 30% node-budget comparison;
- C5--C7: three predictor checkpoints;
- C11--C13: explanation-objective weight ablation;
- C16--C18: stochastic explainer seeds 42, 123, and 2024.

Internal node-token attention was evaluated against shuffled and uniform
controls. It did not improve the final explanation method and is retained only
as an auditable negative-control experiment.

## Rebuilding statistics

```bash
"$PYTHON" -m scripts.aggregate_optimal_subgraph_study
"$PYTHON" scripts/aggregate_natural_strong_baseline_statistics.py
"$PYTHON" scripts/aggregate_stochastic_explainer_seeds.py
"$PYTHON" scripts/aggregate_explanation_objective_ablation.py
"$PYTHON" scripts/aggregate_explanation_truth_statistics.py \
  --summary artifacts/explanation_truth/C8_transformation_truth_strong_baselines_seed42/summary.json \
  --summary artifacts/explanation_truth/C10_codenet_transformation_truth_strong_baselines_seed42/summary.json \
  --summary artifacts/explanation_truth/C15_codenet_negative_pair_transformation_truth_seed42/summary.json
"$PYTHON" scripts/analyze_explanation_runtime_scaling.py
```

See [ARTIFACTS.md](docs/ARTIFACTS.md) for the evidence index and
[REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) for the complete protocol.

## Citation and license

Insert the final paper metadata and repository URL using
[PUBLICATION_LINKS.md](docs/PUBLICATION_LINKS.md). Original repository material
is released under the MIT License. Upstream code and data are not relicensed;
see [THIRD_PARTY.md](docs/THIRD_PARTY.md).

