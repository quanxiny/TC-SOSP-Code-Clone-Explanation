# Reproduction notes

This checkout is pinned to upstream commit
`23a20b7e5f27a217a966401c6c969150bfa023dc`.  The preprocessing checkout next
to it is pinned to `684b9b8128174b704d323e13341385e75f29da7d`.

## Published GCJ/CFG configuration

The repository includes 1,665 GCJ Java files, 1,664 vectorized CFG JSON
files, and the released split.  `train11.txt` is the balanced training set used by
the supplied `main.py`: 176,699 positive and 176,699 negative pairs.  The
validation and test sets contain 13,695 pairs each.

The runner defaults match Table 3 of the paper: 16-dimensional token vectors,
Adam with learning rate 0.001 and weight decay 5e-4, 16 GAT heads, four PNIAT
heads (implemented inside `SingleNodeAttentionLayer`), GAT dropout 0.1, focal
loss alpha 1/gamma 2, batch size 64, and a two-layer BiLSTM with 128 hidden
units.  The full paper run is 100 epochs.

## Environment

From this repository:

```bash
bash scripts/setup_environment.sh
```

PyTorch 1.8 and the matching PyG wheels require CUDA 11.1 libraries.  The run
wrapper sets their runtime library path automatically.  The same environment
also installs JDK 8, which is required by the preprocessing repository's
Gradle 4.7 wrapper.

## Verified preprocessing run

From the sibling `TinyPDG-DataPreprocessingVersion` checkout:

```bash
JAVA_HOME=../.conda/codegraph4cc \
PATH=../.conda/codegraph4cc/bin:/usr/bin:/bin \
./gradlew clean preprocessingSmoke --no-daemon \
  -Pinput=googlejam1.p006.A.java \
  -Poutput=artifacts/preprocessing_smoke
```

This builds TinyPDG, trains fresh 16-dimensional CFG and PDG Word2Vec models
from the checked-in corpora, and emits DOT, plain JSON, and vector JSON for one
Java file.  Unknown tokens are represented by zero vectors rather than invalid
JSON `null` values.  The checked-in `cfg_model.bin` is 32-dimensional, so it is
not used for the paper-compatible smoke output.

## Verified smoke run

```bash
bash scripts/run_reproduction.sh \
  --epochs 1 \
  --train-limit 64 \
  --eval-limit 128 \
  --output-dir artifacts/gcj_cfg_smoke
```

This is an execution check, not a paper-result comparison: 64 training pairs
are not enough for the model to converge.  On the local A100 run, 58 pairs
remained after invalid graphs were skipped; the one-epoch checkpoint produced
macro precision 0.4228, recall 0.5000, and F1 0.4581 over 123 usable test pairs.
Reloading the checkpoint through the separate fast encoder/decoder path gave
exactly the same output as the combined training model for a checked pair
(maximum absolute difference 0.0).

## Paper/release data reconciliation

The paper does not describe damaged graphs or a policy for skipping failed
preprocessing. Section 4.3 says all source fragments are converted once before
training, and Section 5.1/Table 2 describe statistics after preprocessing.
There is an internal count inconsistency: Section 5.1 and Table 2 say 1,669 GCJ
files, while Table 6 reports preprocessing 1,665 files. The public checkout
contains 1,665 files, matching Table 6.

The concatenated public JSON files are recoverable: each concatenated object is
one method graph emitted by the legacy writer. Merging these objects as
disconnected method subgraphs gives an average of 37.43 nodes and 43.93 edges
per file, nearly identical to Table 2's 37.34 and 43.89. This is evidence that
the paper used file-level multi-method graphs and that the public serialization,
not the intended experimental dataset, is defective.

Run the complete repair with:

```bash
bash scripts/rebuild_repaired_gcj_cfg.sh
```

The repair parses every concatenated object, reindexes and merges its methods,
and reconstructs the one absent graph (`googlejam6.p247.B.java`) in the same
released 16-dimensional embedding space. The token-to-vector lookup is recovered
by aligning TinyPDG plain graphs with the 1,664 released graphs; no conflicting
token vectors and no unknown tokens were found for the absent graph. The result
contains 1,665 valid JSON files and all released train/valid/test pairs load.

## Two formal protocols

The released `train11.txt` is balanced, but its source set overlaps 136
validation fragments and 129 test fragments. This contradicts the paper's
8:1:1 fragment split. `trainpos.txt` and `trainneg.txt` use the correct 1,333
training fragments and are disjoint from the 166 validation and 166 test
fragments. Build the paper-described balanced training set with:

```bash
python scripts/build_paper_protocol_split.py \
  --output artifacts/paper_protocol/train_balanced_seed1337.txt
```

The formal reproduction therefore records both protocols:

```bash
# Paper-described, leakage-free protocol
CUDA_VISIBLE_DEVICES=0 bash scripts/run_batched_reproduction.sh \
  --epochs 100 \
  --graph-batch-size 128 \
  --train-split artifacts/paper_protocol/train_balanced_seed1337.txt \
  --output-dir artifacts/formal_paper_protocol_seed1337 \
  --resume

# Released main.py protocol, including its split overlap
CUDA_VISIBLE_DEVICES=1 bash scripts/run_batched_reproduction.sh \
  --epochs 100 \
  --graph-batch-size 128 \
  --train-split DataSetJsonVec/GCJ/javadata/train11.txt \
  --output-dir artifacts/formal_release_code_protocol_seed1337 \
  --resume
```

The batched runner replaces the dense all-node-pairs GAT calculation with the
algebraically equivalent edge-only form and batches disconnected graphs. On a
checked two-graph inference batch, its graph embeddings differ from the dense
release by at most 4.46e-4. This optimization makes the 100-epoch experiment
practical while retaining the released parameters, attention equations, focal
loss, and optimizer.

## Full paper run

```bash
bash scripts/run_reproduction.sh \
  --epochs 100 \
  --output-dir artifacts/gcj_cfg_full
```

The paper reports two days for GCJ training on an RTX 3090.  Checkpoints and a
machine-readable `summary.json` are written below the selected output folder.
To re-evaluate a checkpoint without training:

```bash
bash scripts/run_reproduction.sh \
  --mode eval \
  --checkpoint artifacts/gcj_cfg_full/epoch_100.pt \
  --output-dir artifacts/gcj_cfg_eval
```

The paper reports macro precision 0.995, recall 0.997, and F1 0.996 for GCJ
with CFGs.  Exact equality is not guaranteed because the released training
code does not publish its random seed or trained checkpoints.

There is also a released-data discrepancy.  Across the 1,400 unique graphs
referenced by `train11.txt`, `valid.txt`, and `test.txt`, 76 vector files are
concatenations of multiple JSON objects and one vector file is absent.  The
upstream loader catches these errors silently and skips every affected pair.
With the loader's multi-digit folder bug fixed, 316,717/353,398 training pairs,
12,403/13,695 validation pairs, and 12,880/13,695 test pairs are usable.  This
does not match Table 2's claim that all 1,669 GCJ fragments were preprocessed,
so the exact paper dataset is not fully recoverable from the public checkout.
The audit can be repeated with:

```bash
python scripts/audit_gcj_release.py --output artifacts/gcj_release_audit.json
```

## Upstream reproducibility gaps

- The README says `requriements.txt`; the checked-in file is
  `requirements.txt`.
- `main.py` hard-codes GCJ/CFG paths and evaluates every epoch.
- `main_test_fast.py` hard-codes checkpoint index 1, but no trained checkpoint
  is included.
- `CodeCloneDetection` instantiates an unused `lin1` layer (8,976 parameters),
  so the training model has 1,143,943 parameters while the fast
  encoder/decoder evaluation path uses 1,134,967.
- The preprocessing README omits the build/run commands and its entry points
  hard-code the input/output paths.
- The main repository releases GCJ CFG vectors but not its GCJ PDG vectors.
- BCB source and pair files are included in `BCB.zip`, but the vectorized BCB
  graphs used by the model are not included in the main repository.
