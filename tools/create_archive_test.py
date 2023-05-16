#
# Copyright 2023 The Cobalt Authors. All Rights Reserved.
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
"""Tests for archiver launcher"""

import tools.create_archive
import unittest
import tempfile
import os
import tarfile

# pylint: disable=missing-class-docstring


# pylint: disable=protected-access
class TestArchive(unittest.TestCase):

  def setUp(self):
    # pylint: disable=consider-using-with
    self.tmpdir = tempfile.TemporaryDirectory()
    self.dir1 = os.path.abspath(os.path.join(self.tmpdir.name, 'dir1/'))
    self.dir2 = os.path.abspath(os.path.join(self.tmpdir.name, 'dir2/'))
    test_file = os.path.abspath(
        os.path.join(self.tmpdir.name, 'dir1', 'test.txt'))
    ignored_file = os.path.join(self.tmpdir.name, 'dir2', 'test.ninja_log')
    os.makedirs(self.dir1)
    os.makedirs(self.dir2)
    with open(test_file, 'a', encoding='utf-8') as f:
      f.write('testcontent')
    with open(ignored_file, 'a', encoding='utf-8') as f:
      f.write('testcontent')

  def test_compress(self):
    self.dest = os.path.join(self.tmpdir.name, 'dest/final.tar.gz')
    tools.create_archive._CreateCompressedArchive([self.dir1, self.dir2],
                                                  self.dest, '*.txt', False)
    with tarfile.open(self.dest, 'r:gz') as tar:
      objects = [tarinfo.name for tarinfo in tar]
      self.assertIn('dir1/test.txt', objects)
      self.assertNotIn('dir2/test.ninja_log', objects)

  def test_compress_parallel(self):
    self.dest = os.path.join(self.tmpdir.name, 'dest/final.tar.xz')
    tools.create_archive._CreateCompressedArchive([self.dir1, self.dir2],
                                                  self.dest, '*.txt', False,
                                                  True)
    with tarfile.open(self.dest, 'r:xz') as tar:
      objects = [tarinfo.name for tarinfo in tar]
      self.assertIn('dir1/test.txt', objects)
      self.assertNotIn('dir2/test.ninja_log', objects)
