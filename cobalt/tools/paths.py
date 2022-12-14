#
# Copyright 2016 The Cobalt Authors. All Rights Reserved.
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
#
"""Constants and functions for commonly referenced paths."""

from os import path

from starboard.tools import paths

STARBOARD_ROOT = paths.STARBOARD_ROOT

REPOSITORY_ROOT = paths.REPOSITORY_ROOT

COBALT_ROOT = path.join(REPOSITORY_ROOT, 'cobalt')

BUILD_ROOT = path.join(COBALT_ROOT, 'build')

THIRD_PARTY_ROOT = paths.THIRD_PARTY_ROOT

BUILD_OUTPUT_ROOT = paths.BUILD_OUTPUT_ROOT


def BuildOutputDirectory(platform, config):
  return paths.BuildOutputDirectory(platform, config)
