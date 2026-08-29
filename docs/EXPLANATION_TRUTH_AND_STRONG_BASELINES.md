# Explanation truth and strong-baseline protocol

Status: GCJ natural-pair evaluation and GCJ/CodeNet transformation evaluations
are complete. The computational evidence is frozen; real blinded expert ratings
remain pending. No test split is used.

## Transformation-derived truth

Thirty independent GCJ validation programs were selected by a fixed SHA-256
ranking. Each retained program has three variants:

1. the original validation source;
2. a consistent identifier alpha-renaming;
3. the alpha-renamed program plus a zero-valued guarded empty print block.

Every original and both transforms compile in isolation. The TinyPDG CFG
pipeline generated all 90 files without failure. After inverse alpha-renaming,
the original and alpha CFGs have identical node text, node order, and topology.
Sequence alignment maps every alpha node into the dead-code variant and leaves
exactly three introduced CFG nodes per program. Those unmatched nodes are known
semantic distractors.

This creates two auditable axes:

- exact explanation-node correspondence under alpha-renaming;
- rejection of known irrelevant dead-code nodes.

It does not assert that a unique, complete human rationale exists. Human expert
annotations remain a separate supplement; no scores are imputed from the
transformation truth.

Artifacts:

- `external_data/explanation_truth/gcj_transformations/transformation_manifest.json`
- `external_data/explanation_truth/gcj_transformations/explanation_truth_manifest.json`
- `external_data/explanation_truth/gcj_transformations/cfg16_normalized_report.json`

The same frozen construction was independently repeated on 30 Project CodeNet
T3 validation programs: 90/90 graphs generated, zero normalization failures,
and exactly three known irrelevant nodes per transformed program. Its artifacts
are under `external_data/explanation_truth/codenet_transformations/`; C10 uses
the frozen seed-42 CodeNet Fragment Replay checkpoint. This is a genuine
cross-dataset replication rather than a second GCJ sample.

To avoid validating transformation truth only on positive clone pairs, a second
GCJ validation benchmark uses 20 frozen natural non-clone pairs on which the
predictor was already correct in C1. The 40 programs are not reused across
pairs, and all original/transformed sources compile. Both sides are
alpha-renamed and then receive the same irrelevant guarded block, creating an
adversarial common lexical distractor. The benchmark measures sidewise
selection/relation correspondence, rejection of all six known dead nodes per
pair, prediction invariance, and faithfulness. TinyPDG generated 120/120 graphs
with zero normalization failures. A first arbitrary different-problem pairing
was stopped after early records showed that it produced model false positives;
it is excluded rather than relabeled as a negative-decision explanation. The
corrected fixed manifest is
`external_data/explanation_truth/gcj_frozen_negative_pair_transformations/negative_pair_truth_manifest.json`;
C14 was screened before full explanation evaluation. Only 4/20 rebuilt base
pairs remained non-clone predictions and only 2/20 remained non-clones across
all three variants. This reveals a material domain shift between the released
GCJ graph vectors and CFGs regenerated with the available 16-dimensional
preprocessing model. The sample is insufficient, so C14 is stopped and excluded
from method-effect tables. The full negative result is retained in
`external_data/explanation_truth/gcj_frozen_negative_pair_transformations/rebuilt_prediction_screen.json`.
Negative-decision behavior is instead evaluated on the 50 unmodified natural
validation negatives in C9.

The same negative-pair construction is viable on CodeNet because its continual
checkpoint was trained on the current preprocessing representation. All 15/15
disjoint different-problem pairs remain non-clones for the original, bilateral
alpha-renamed, and bilateral-dead-code variants. C15 therefore evaluates all
four methods on this independent negative-decision metamorphic set; its fixed
eligibility record is
`external_data/explanation_truth/codenet_transformations/negative_pair_prediction_screen.json`.

## Strong baselines

The formal comparison uses the same symmetric pair predictor, 20% nodes per
graph, and identical feature-masking intervention for:

- symmetric Grad×Input;
- a GNNExplainer mutual-information objective adapted to two node masks;
- SubgraphX-style discrete MCTS with Monte-Carlo Shapley reward adapted to one
  coalition spanning both CFGs;
- the task-conditioned semantic optimal subgraph pair method.

The adaptations are named explicitly because the released encoder does not
expose PyG `MessagePassing` edge-mask hooks and the prediction consumes two
graphs. They are not represented as unmodified official implementations.

Primary method references:

- GNNExplainer, NeurIPS 2019: <https://openreview.net/forum?id=pVywBxmyYC>
- SubgraphX, ICML 2021: <https://proceedings.mlr.press/v139/yuan21c.html>
- PGExplainer, NeurIPS 2020 (next parametric candidate):
  <https://proceedings.neurips.cc/paper_files/paper/2020/hash/e37b08dd3015330dcbb5d6663667b8b8-Abstract.html>
- GOAt, ICLR 2024 (architecture-specific reference):
  <https://proceedings.iclr.cc/paper_files/paper/2024/hash/92ee07d8a2c8f5ec08eff83f9eff0c1b-Abstract-Conference.html>

## Metrics

Correspondence Jaccard and relation precision are higher-is-better. Selection
recall and attribution share on known irrelevant nodes are lower-is-better.
Fidelity reports necessity drop and absolute sufficiency gap. All method
differences use paired, program-level bootstrap intervals.

## GCJ transformation results

The frozen C8 run evaluated all four methods on the same 30 programs. Values
below are means at the fixed 20% per-graph node budget.

| Method | Alpha correspondence Jaccard | Dead-variant correspondence Jaccard | Dead-node selection recall (lower is better) | Necessity | Absolute sufficiency gap | Seconds/program |
|---|---:|---:|---:|---:|---:|---:|
| Symmetric Grad×Input | 0.6871 | 0.7377 | 0.0444 | 0.0226 | 0.0945 | 0.855 |
| Adapted GNNExplainer | 0.3435 | 0.5622 | 0.2778 | 0.0351 | 0.0986 | 3.370 |
| Adapted SubgraphX | 0.3390 | 0.3700 | 0.0667 | **0.1552** | 0.1817 | 22.824 |
| TC-SOSP | **0.7049** | **0.7844** | **0.0222** | 0.0730 | **0.0396** | 1.125 |

The table exposes a genuine Pareto trade-off rather than hiding it. Relative
to symmetric Grad×Input, TC-SOSP improves mean necessity by 0.0504 (paired
bootstrap 95% CI `[0.0258, 0.0794]`) and reduces absolute sufficiency gap by
0.0549 (`[0.0186, 0.0987]`). Its correspondence improvements over Grad×Input
are positive in mean but their intervals cross zero.

Relative to adapted GNNExplainer, TC-SOSP improves alpha correspondence by
0.3614 (`[0.2725, 0.4596]`), dead-variant correspondence by 0.2222
(`[0.1569, 0.2937]`), dead-node rejection by 0.2556
(`[0.1889, 0.3222]`), necessity by 0.0379 (`[0.0022, 0.0727]`), and absolute
sufficiency gap by 0.0590 (`[0.0341, 0.0851]`).

Relative to adapted SubgraphX, TC-SOSP has much higher alpha and dead-variant
correspondence (deltas 0.3658 and 0.4144, both intervals excluding zero) and a
0.1421 lower absolute sufficiency gap (`[0.0810, 0.2079]`), but SubgraphX has
higher necessity by 0.0822 (`[0.0291, 0.1471]`) and a lower attribution share
on the injected dead nodes. Consequently the defensible claim is a more
correspondence-consistent and sufficient semantic graph-pair explanation, not
universal dominance on every faithfulness axis.

A stricter two-sided paired Wilcoxon analysis with Holm correction across all
18 baseline/endpoint tests preserves the TC-SOSP versus Grad×Input necessity
(`p_Holm=2.86e-5`) and sufficiency (`p_Holm=0.0060`) results. It also preserves
the correspondence and sufficiency advantages over SubgraphX, while confirming
SubgraphX's necessity advantage (`p_Holm=0.0107`). The GNNExplainer
correspondence, distractor-rejection, and sufficiency results survive this
family-wide correction; its necessity comparison does not. Full signed-rank
effects and corrected p-values are stored in
`artifacts/comparisons/C_transformation_truth_paired_statistics.json`.

Machine-readable evidence is in
`artifacts/explanation_truth/C8_transformation_truth_strong_baselines_seed42/summary.json`.

## Independent Project CodeNet transformation results

C10 repeats the frozen 30-program protocol with Project CodeNet T3 validation
programs and a CodeNet continual-model checkpoint. All 30/30 programs and four
methods completed.

| Method | Alpha correspondence Jaccard | Dead-variant correspondence Jaccard | Dead-node selection recall | Necessity | Absolute sufficiency gap | Seconds/program |
|---|---:|---:|---:|---:|---:|---:|
| Symmetric Grad×Input | 0.6655 | 0.6164 | 0.0556 | 0.1946 | 0.0718 | 0.870 |
| Adapted GNNExplainer | 0.2769 | 0.5360 | 0.1111 | 0.2122 | 0.2650 | 3.446 |
| Adapted SubgraphX | 0.3415 | 0.3093 | 0.0667 | **0.3764** | 0.1968 | 19.320 |
| TC-SOSP | **0.7113** | **0.6832** | **0.0000** | 0.2800 | **0.0531** | 0.965 |

The independent result replicates the same main trade-off. Against
Grad×Input, TC-SOSP improves necessity by 0.0854 (paired bootstrap 95% CI
`[0.0492, 0.1243]`; 18-endpoint `p_Holm=0.00010`); its mean correspondence and
sufficiency changes are favorable but their intervals or corrected tests do
not exclude zero. Against GNNExplainer it has higher correspondence, rejects
more dead nodes, and reduces sufficiency gap; the alpha-correspondence,
dead-node selection, and sufficiency results survive family-wide Holm
correction. Against SubgraphX, both correspondence axes and sufficiency survive
Holm correction, while SubgraphX again has higher mean necessity. TC-SOSP never
selects an injected dead node, but its continuous attribution mass on those
nodes is higher than SubgraphX's; that negative secondary result also survives
Holm correction and is retained explicitly.

Evidence:
`artifacts/explanation_truth/C10_codenet_transformation_truth_strong_baselines_seed42/summary.json`.
The combined GCJ/CodeNet signed-rank analysis is
`artifacts/comparisons/C_transformation_truth_paired_statistics.json`.

## Natural GCJ clone/non-clone results

C9 evaluates 100 fixed validation pairs (50 clone and 50 non-clone) at the same
20% per-graph budget. The predictor is correct on 99/100 pairs. The explanation
comparison uses all 100 predictions rather than filtering the one error after
seeing method results.

| Method | Necessity | Absolute sufficiency gap | Swap Jaccard | Seconds/pair |
|---|---:|---:|---:|---:|
| Symmetric Grad×Input | 0.1731 | 0.0376 | **1.0000** | **0.302** |
| Adapted GNNExplainer (3-seed mean) | 0.0358 | 0.3301 | 0.9993 | 3.489 |
| Adapted SubgraphX (3-seed mean) | 0.2282 | 0.0232 | 0.9956 | 23.805 |
| TC-SOSP | **0.3088** | **0.0069** | **1.0000** | 0.559 |

Against Grad×Input, TC-SOSP improves necessity by 0.1356 (problem-pair cluster
bootstrap 95% CI `[0.0754, 0.1764]`) and reduces absolute sufficiency gap by
0.0306 (`[0.0006, 0.0593]`). Against the per-pair three-seed average adapted
GNNExplainer, the corresponding improvements are 0.2730 (`[0.1385, 0.3799]`)
and 0.3231 (`[0.0941, 0.4750]`). Against the three-seed average adapted
SubgraphX, they are 0.0806 (`[0.0387, 0.1144]`) and 0.0163
(`[0.0051, 0.0344]`). The four stochastic-baseline core comparisons remain
significant after two-sided paired Wilcoxon tests and Holm correction across
two baselines by three endpoints; adjusted p-values are at most `3.01e-7`.
The deterministic Grad×Input comparison remains significant under the original
nine-endpoint family. Swap deltas are not significant.

The effect is not confined to clone decisions. Against Grad×Input, TC-SOSP's
necessity improvement is 0.0753 on the 50 natural non-clones and 0.1960 on the
50 natural clones; the label-specific cluster intervals exclude zero. Its
sufficiency-gap reduction is 0.0046 for non-clones and 0.0567 for clones; the
clone-only cluster interval crosses zero, so this stratified secondary result is
not overstated. Against adapted SubgraphX, both necessity and sufficiency mean
improvements have positive cluster intervals in each label stratum.

Evidence:
`artifacts/pilots/C9_natural_validation_strong_baselines_seed42/summary.json`
and
`artifacts/comparisons/C9_natural_strong_baseline_paired_statistics_validation.json`.

### Stochastic explainer-seed robustness

The adapted GNNExplainer and SubgraphX baselines were additionally evaluated
with explainer seeds 42, 123, and 2024 on all 100 pairs. The predictor,
manifest, node budget, optimization steps, MCTS visits, and Shapley samples are
fixed. GNNExplainer uses the PyG-style Gaussian mask-logit initialization with
standard deviation 0.1. SubgraphX seed 42 preserves the original frozen
content-hash trajectory; seeds 123 and 2024 add an explicit canonical graph-pair
seed. The maximum repeated-inference base-probability drift is `9.66e-6`, with
identical predictions and targets.

TC-SOSP's necessity/sufficiency mean advantage is positive for every explainer
seed. In the worst seed it is `+0.2661/+0.3156` against GNNExplainer and
`+0.0764/+0.0103` against SubgraphX. Every seed-specific problem-pair cluster
interval for these four core effects excludes zero. Explainer seeds are not
treated as 300 independent samples: the primary analysis averages each
stochastic baseline over seeds within pair before the 100-pair clustered test.

The selected nodes themselves are seed-sensitive. Mean three-seed pairwise
selection Jaccard is 0.5026 for GNNExplainer and 0.4654 for SubgraphX, and no
pair has exactly the same bilateral selection across all three seeds. Thus the
method-effect conclusion is robust while individual stochastic baseline
rationales are not. Full evidence is
`artifacts/comparisons/C16_C18_stochastic_explainer_seed_robustness_validation.json`.

### Empirical runtime scaling

Across the same 100 pairs, TC-SOSP takes 0.559 seconds/pair on average, versus
three-seed means of 3.489 for adapted GNNExplainer and 23.805 for adapted
SubgraphX: mean runtime ratios of 6.2x and 42.6x. TC-SOSP's mean time rises from 0.519 seconds in the
smallest total-node quartile to 0.594 seconds in the largest. SubgraphX rises
from 22.114 to 25.510 seconds. These are empirical single-GPU measurements,
not asymptotic complexity claims. Full quartiles, rank correlations, and OLS
descriptors are stored in
`artifacts/comparisons/C9_explanation_runtime_scaling_validation.json`.

## CodeNet negative-decision metamorphic results

C15 completed all 15 disjoint different-problem pairs. Every base and
transformed prediction remains a correct non-clone.

| Method | Base-to-alpha correspondence | Alpha-to-dead correspondence | Dead-node selection recall | Necessity | Absolute sufficiency gap |
|---|---:|---:|---:|---:|---:|
| Symmetric Grad×Input | **0.6079** | **0.6868** | 0.0556 | 0.1075 | 0.0657 |
| Adapted GNNExplainer | 0.3273 | 0.4658 | 0.1444 | 0.0357 | 0.1711 |
| Adapted SubgraphX | 0.3858 | 0.4192 | 0.0667 | 0.1890 | 0.0330 |
| TC-SOSP | 0.5438 | 0.5936 | **0.0222** | **0.3002** | **0.0189** |

For negative decisions, TC-SOSP's contrastive-difference construction changes
the positive-pair trade-off: it now has the highest necessity and lowest
sufficiency gap. Against Grad×Input, necessity improves by 0.1927 (bootstrap
95% CI `[0.1253, 0.2715]`; 18-endpoint `p_Holm=0.00110`) and sufficiency gap
falls by 0.0468 (`[0.0095, 0.0931]`), while Grad×Input retains higher mean
transformation correspondence. Against GNNExplainer, both correspondence means,
dead-node rejection, necessity, and sufficiency are favorable; alpha
correspondence, necessity, and sufficiency survive strict Holm correction.
Against SubgraphX, all four primary mean deltas are favorable and their paired
bootstrap intervals exclude zero, but the n=15 signed-rank tests do not survive
correction across all 18 endpoints. TC-SOSP again assigns more continuous mass
to dead nodes than SubgraphX despite selecting fewer of them, so selection and
soft attribution are reported separately.

Evidence:
`artifacts/explanation_truth/C15_codenet_negative_pair_transformation_truth_seed42/summary.json`.

## Blinded expert supplement

Three independently shuffled, method-blinded review packs are ready under
`artifacts/expert_annotation/C8_gcj_rater{1,2,3}/`. Each contains all 240
program/variant/method items, selected node statements, collapsible complete
sources, a fixed ordinal rating form, and per-item active review time. Method
keys are stored separately in
`private_method_key.json` and must remain unopened until the completed forms
are frozen and hashed. This infrastructure closes the protocol gap, but the
human-evaluation result remains pending until real independent experts provide
ratings; it is not counted as a completed experiment.

Three additional independently shuffled natural-pair packs are ready under
`artifacts/expert_annotation/C9_natural_rater{1,2,3}/`. Each pack contains the
same fixed 20 correct clone and 20 correct non-clone decisions, crossed with all
four methods (160 items per rater). The form asks experts to judge the shared
semantic core for clone decisions and discriminative differences for non-clone
decisions. Each public pack now contains a standalone offline visual
questionnaire with browser-local autosave, 20-item sessions, pause-aware active
timing, unanswered/flag filters, JSON backup/restore, analyzer-compatible CSV
export, final locking, and SHA-256 attestation. The three method keys have mode
`600`; no rating has been generated or inferred. After at least two real raters
return frozen forms, the existing analysis verifies web-export hashes and
reports weighted inter-rater kappa, method summaries, active review time, and
paired program-level bootstrap intervals.

For research efficiency, C9 is the primary human study because it directly
covers natural clone and non-clone decisions; reviewers do not need to complete
both C8 and C9 for the main claim. Key-free C9 archives are under
`artifacts/expert_annotation/public_packages/`, with frozen hashes in
`SHA256SUMS`. The C8 packs remain an optional transformation-focused secondary
study. Only the key-free archive assigned to a rater should be distributed.
A planning estimate is 45--90 active seconds per item, or approximately 2--4
hours per rater split into eight sessions; a 10--20 item independent pilot must
calibrate this estimate. Operational details are frozen in
`docs/EXPERT_BLIND_REVIEW_WEB_GUIDE.md`.
