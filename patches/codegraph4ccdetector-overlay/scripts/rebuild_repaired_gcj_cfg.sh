#!/usr/bin/env bash
set -euo pipefail

repository_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace_dir="$(cd "${repository_dir}/.." && pwd)"
preprocessor_dir="${workspace_dir}/TinyPDG-DataPreprocessingVersion"
environment_prefix="${CODEGRAPH_ENV_PREFIX:-${workspace_dir}/.conda/codegraph4cc}"
extract_dir="${preprocessor_dir}/artifacts/gcj_cfg_extract"
repaired_dir="${repository_dir}/artifacts/gcj_cfg16_repaired"

cd "${preprocessor_dir}"
JAVA_HOME="${environment_prefix}" \
PATH="${environment_prefix}/bin:/usr/bin:/bin" \
./gradlew clean preprocessDataset --no-daemon \
  -Pinput="${repository_dir}/googlejam4_src" \
  -PgraphType=cfg \
  -Pmodel="${preprocessor_dir}/cfg_model.bin" \
  -Poutput="${extract_dir}"

"${environment_prefix}/bin/python" scripts/repair_gcj_cfg.py \
  --source-dir "${repository_dir}/googlejam4_src" \
  --plain-dir "${extract_dir}/outPut_cfg/codeJson" \
  --released-vector-dir "${repository_dir}/DataSetJsonVec/GCJ/dataSetCfgGCJ16" \
  --output-dir "${repaired_dir}" \
  --report "${repository_dir}/artifacts/gcj_cfg16_repaired_report.json"

cd "${repository_dir}"
"${environment_prefix}/bin/python" scripts/audit_gcj_release.py \
  --vector-dir "${repaired_dir}" \
  --output artifacts/gcj_cfg16_repaired_audit.json
