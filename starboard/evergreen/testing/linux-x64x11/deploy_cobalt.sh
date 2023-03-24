#!/bin/bash
#
# Copyright 2020 The Cobalt Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

function deploy_cobalt() {
  if [[ -z "${OUT}" ]]; then
    log "info" "Please set the environment variable 'OUT'"
    exit 1
  fi

  staging_dir="${OUT}"

  echo " Checking '${staging_dir}'"

  PATHS=("${staging_dir}/loader_app"                                                \
         "${staging_dir}/content/app/cobalt/lib/libcobalt${SYSTEM_IMAGE_EXTENSION}" \
         "${staging_dir}/content/app/cobalt/content/")

  for file in "${PATHS[@]}"; do
    if [[ ! -e "${file}" ]]; then
      echo " Failed to find '${file}'"
      exit 1
    fi
  done

  echo " Required files were found within '${staging_dir}'"

  echo " Deploying Cobalt on local device"

  echo " Generating HTML test directory"
  eval "mkdir -p ${staging_dir}/content/app/cobalt/content/web/tests/" 1> /dev/null

  echo " Copying HTML test files to HTML test directory"
  eval "cp ${1}/../tests/*.html ${staging_dir}/content/app/cobalt/content/web/tests/" 1> /dev/null

  clear_storage

  echo " Successfully deployed!"
}
