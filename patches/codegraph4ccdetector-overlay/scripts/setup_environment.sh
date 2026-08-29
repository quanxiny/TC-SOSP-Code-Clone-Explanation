#!/usr/bin/env bash
set -euo pipefail

repository_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace_dir="$(cd "${repository_dir}/.." && pwd)"
environment_prefix="${CODEGRAPH_ENV_PREFIX:-${workspace_dir}/.conda/codegraph4cc}"

if [[ ! -x "${environment_prefix}/bin/python" ]]; then
  conda create \
    --override-channels \
    -c https://repo.anaconda.com/pkgs/main \
    --prefix "${environment_prefix}" \
    python=3.8 pip=24.2 pysocks -y
fi

conda install \
  --override-channels \
  -c https://conda.anaconda.org/conda-forge \
  -c https://repo.anaconda.com/pkgs/main \
  --prefix "${environment_prefix}" \
  python=3.8 pip=24.2 pysocks cudatoolkit=11.1.1 openjdk=8 -y

python_bin="${environment_prefix}/bin/python"
"${python_bin}" -m pip install \
  'torch==1.8.0+cu111' \
  -f https://download.pytorch.org/whl/torch_stable.html
"${python_bin}" -m pip install \
  'torch-scatter==2.0.8' \
  'torch-sparse==0.6.12' \
  -f https://data.pyg.org/whl/torch-1.8.0+cu111.html
"${python_bin}" -m pip install \
  'numpy==1.19.2' \
  'scikit-learn==1.1.2' \
  'torch-geometric==2.0.1' \
  'tqdm==4.62.3' \
  'utils==1.0.1'

echo "Environment ready: ${environment_prefix}"
