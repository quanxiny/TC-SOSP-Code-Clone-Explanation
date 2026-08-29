#!/usr/bin/env bash
set -euo pipefail

repository_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace_dir="$(cd "${repository_dir}/.." && pwd)"
detector_dir="${workspace_dir}/CodeGraph4CCDetector"
preprocessor_dir="${workspace_dir}/TinyPDG-DataPreprocessingVersion"
detector_commit="23a20b7e5f27a217a966401c6c969150bfa023dc"
preprocessor_commit="684b9b8128174b704d323e13341385e75f29da7d"

checkout() {
  local url="$1"
  local commit="$2"
  local destination="$3"

  if [[ ! -e "${destination}" ]]; then
    git clone "${url}" "${destination}"
    git -C "${destination}" checkout --detach "${commit}"
    return
  fi
  if [[ ! -d "${destination}/.git" ]]; then
    echo "Existing path is not a Git checkout: ${destination}" >&2
    exit 1
  fi
  local current
  current="$(git -C "${destination}" rev-parse HEAD)"
  if [[ "${current}" != "${commit}" ]]; then
    echo "Refusing to modify ${destination}: expected ${commit}, found ${current}" >&2
    exit 1
  fi
}

apply_patch_once() {
  local destination="$1"
  local patch_file="$2"
  if git -C "${destination}" apply --reverse --check "${patch_file}" >/dev/null 2>&1; then
    return
  fi
  git -C "${destination}" apply --check "${patch_file}"
  git -C "${destination}" apply "${patch_file}"
}

checkout \
  https://github.com/HduDBSI/CodeGraph4CCDetector.git \
  "${detector_commit}" "${detector_dir}"
checkout \
  https://github.com/QuanixnYang/TinyPDG-DataPreprocessingVersion.git \
  "${preprocessor_commit}" "${preprocessor_dir}"

apply_patch_once "${detector_dir}" \
  "${repository_dir}/patches/codegraph4ccdetector.patch"
apply_patch_once "${preprocessor_dir}" \
  "${repository_dir}/patches/tinypdg-preprocessing.patch"

cp -a "${repository_dir}/patches/codegraph4ccdetector-overlay/." "${detector_dir}/"
cp -a "${repository_dir}/patches/tinypdg-overlay/." "${preprocessor_dir}/"
chmod +x "${detector_dir}"/scripts/*.sh

echo "Pinned upstream dependencies are ready in ${workspace_dir}"

