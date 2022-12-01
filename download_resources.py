#!/usr/bin/env python
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
"""Downloads tools to assist in developing Cobalt."""

import logging
import os
import platform
import subprocess
try:
  import urllib.request as urllib
except ImportError:
  import urllib2 as urllib

from tools import download_from_gcs


def DownloadClangFormat(force=False):
  clang_format_sha_path = os.path.join('buildtools', '{}', 'clang-format')

  system = platform.system()
  if system == 'Linux':
    clang_format_sha_path = clang_format_sha_path.format('linux64')
  elif system == 'Darwin':
    clang_format_sha_path = clang_format_sha_path.format('mac')
  elif system == 'Windows':
    clang_format_sha_path = clang_format_sha_path.format('win') + '.exe'
  else:
    logging.error('Unknown system: %s', system)
    return

  download_from_gcs.MaybeDownloadFileFromGcs('chromium-clang-format',
                                             clang_format_sha_path + '.sha1',
                                             clang_format_sha_path, force)


def Download_GerritCommitMsgHook(force=False):
  git_dir = subprocess.check_output(['git', 'rev-parse', '--git-common-dir'
                                    ]).strip().decode('utf-8')
  git_commit_msg_hook_path = os.path.join(git_dir, 'hooks', 'commit-msg')

  if not force and os.path.exists(git_commit_msg_hook_path):
    logging.info('commit-msg hook found, skipping download.')
    return

  hook_url = 'https://gerrit-review.googlesource.com/tools/hooks/commit-msg'
  try:
    res = urllib.urlopen(hook_url)
  except urllib.URLError:
    # pylint:disable=import-outside-toplevel
    from ssl import _create_unverified_context
    context = _create_unverified_context()
    res = urllib.urlopen(hook_url, context=context)

  if not res:
    logging.error('Could not fetch %s', hook_url)
    return

  with open(git_commit_msg_hook_path, 'wb') as fd:
    fd.write(res.read())
  download_from_gcs.AddExecutableBits(git_commit_msg_hook_path)
  logging.info('Gerrit commit-msg hook installed.')


if __name__ == '__main__':
  logging_format = '[%(levelname)s:%(filename)s:%(lineno)s] %(message)s'
  logging.basicConfig(
      level=logging.INFO, format=logging_format, datefmt='%H:%M:%S')

  DownloadClangFormat()
  DownloadGerritCommitMsgHook()
