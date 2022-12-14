#
# Copyright 2017 The Cobalt Authors. All Rights Reserved.
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
"""Sets PYTHONPATH for third_party/blink modules to work correctly."""

from os import path
import sys

_REPO_ROOT = path.abspath(
    path.join(path.dirname(__file__), path.pardir, path.pardir))
_BLINK_PATHS = [
    path.join(_REPO_ROOT, 'third_party', 'blink', 'Tools', 'Scripts'),
    path.join(_REPO_ROOT, 'third_party', 'blink', 'Source', 'bindings',
              'scripts'),
]

if _REPO_ROOT not in sys.path:
  sys.path.insert(0, _REPO_ROOT)

for path in _BLINK_PATHS:
  if path not in sys.path:
    sys.path.append(path)
