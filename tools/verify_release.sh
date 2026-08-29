#!/usr/bin/env bash
set -euo pipefail

repository_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repository_dir}"

python_bin="${PYTHON:-python3}"
"${python_bin}" -m compileall -q research_cli.py scripts tests
"${python_bin}" scripts/validate_configs.py

private_path_pattern='/home/'"yqx/|/Users/"'yqx/'
if rg -n "${private_path_pattern}" .; then
  echo "A private host path remains in the release" >&2
  exit 1
fi

if find . -type f \( -name '*.pt' -o -name '*.pth' -o -name '*.ckpt' \) -print -quit | grep -q .; then
  echo "A checkpoint file is present in the Git release" >&2
  exit 1
fi

for forbidden in expert_annotation private_method_key annotation_form; do
  if find . -iname "*${forbidden}*" -print -quit | grep -q .; then
    echo "Private review material is present: ${forbidden}" >&2
    exit 1
  fi
done

if [[ -f ARTIFACT_SHA256SUMS ]]; then
  sha256sum --check ARTIFACT_SHA256SUMS
fi

if [[ "${1:-}" == "--full" ]]; then
  environment_prefix="${CODEGRAPH_ENV_PREFIX:-$(cd .. && pwd)/.conda/codegraph4cc}"
  if [[ ! -x "${environment_prefix}/bin/python" ]]; then
    echo "Reference environment not found: ${environment_prefix}" >&2
    exit 1
  fi
  LD_LIBRARY_PATH="${environment_prefix}/lib${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}" \
    "${environment_prefix}/bin/python" -m unittest discover -s tests -v
fi

echo "Release verification passed"
