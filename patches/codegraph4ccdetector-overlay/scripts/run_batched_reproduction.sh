#!/usr/bin/env bash
set -euo pipefail

repository_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace_dir="$(cd "${repository_dir}/.." && pwd)"
environment_prefix="${CODEGRAPH_ENV_PREFIX:-${workspace_dir}/.conda/codegraph4cc}"

if [[ ! -x "${environment_prefix}/bin/python" ]]; then
  echo "Missing environment: ${environment_prefix}" >&2
  exit 1
fi

export LD_LIBRARY_PATH="${environment_prefix}/lib${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
export CUBLAS_WORKSPACE_CONFIG=:4096:8
cd "${repository_dir}"
exec "${environment_prefix}/bin/python" reproduce_gcj_batched.py "$@"
