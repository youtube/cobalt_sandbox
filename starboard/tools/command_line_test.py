#!/usr/bin/env python3
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
"""Tests the command_line module."""

import argparse
import os
import unittest

from starboard.build.platforms import PLATFORMS
from starboard.tools import command_line
import starboard.tools.config

_A_CONFIG = starboard.tools.config.GetAll()[0]
_A_PLATFORM = list(PLATFORMS.keys())[0]


def _RestoreMapping(target, source):
  target.clear()
  for key, value in source.items():
    target[key] = value


def _ClearEnviron():
  if 'BUILD_CONFIGURATION' in os.environ:
    del os.environ['BUILD_CONFIGURATION']
  if 'BUILD_TYPE' in os.environ:
    del os.environ['BUILD_TYPE']
  if 'BUILD_PLATFORM' in os.environ:
    del os.environ['BUILD_PLATFORM']


def _CreateParser():
  arg_parser = argparse.ArgumentParser()
  command_line.AddPlatformConfigArguments(arg_parser)
  return arg_parser


def _SetEnvironConfig(config):
  os.environ['BUILD_TYPE'] = config


def _SetEnvironPlatform(platform):
  os.environ['BUILD_PLATFORM'] = platform


def _SetEnvironBuildConfiguration(config, platform):
  os.environ['BUILD_CONFIGURATION'] = f'{platform}_{config}'


def _SetEnviron(config, platform):
  _SetEnvironConfig(config)
  _SetEnvironPlatform(platform)
  _SetEnvironBuildConfiguration(config, platform)


class CommandLineTest(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self.environ = os.environ.copy()
    _ClearEnviron()

  def tearDown(self):
    _RestoreMapping(os.environ, self.environ)
    super().tearDown()

  def testNoEnvironmentRainyDayNoArgs(self):
    arg_parser = _CreateParser()
    with self.assertRaises(SystemExit):
      arg_parser.parse_args([])

  def testNoEnvironmentRainyDayNoConfig(self):
    arg_parser = _CreateParser()
    with self.assertRaises(SystemExit):
      arg_parser.parse_args(['-p', _A_PLATFORM])

  def testNoEnvironmentRainyDayNoPlatform(self):
    arg_parser = _CreateParser()
    with self.assertRaises(SystemExit):
      arg_parser.parse_args(['-c', _A_CONFIG])

  def testNoEnvironmentSunnyDay(self):
    arg_parser = _CreateParser()
    args = arg_parser.parse_args(['-c', _A_CONFIG, '-p', _A_PLATFORM])
    self.assertEqual(_A_CONFIG, args.config)
    self.assertEqual(_A_PLATFORM, args.platform)

  def testDefaultsSunnyDay(self):
    _SetEnviron(_A_CONFIG, _A_PLATFORM)
    arg_parser = _CreateParser()
    args = arg_parser.parse_args([])
    self.assertEqual(_A_CONFIG, args.config)
    self.assertEqual(_A_PLATFORM, args.platform)

  def testDefaultsRainyDayBadConfig(self):
    _SetEnviron('badconfig', _A_PLATFORM)
    arg_parser = _CreateParser()
    with self.assertRaises(SystemExit):
      arg_parser.parse_args([])

  def testDefaultsRainyDayBadPlatform(self):
    _SetEnviron(_A_CONFIG, 'badplatform')
    arg_parser = _CreateParser()
    with self.assertRaises(SystemExit):
      arg_parser.parse_args([])

  def testBadEnvironmentSunnyDay(self):
    _SetEnviron('badconfig', 'badplatform')
    arg_parser = _CreateParser()
    args = arg_parser.parse_args(['-c', _A_CONFIG, '-p', _A_PLATFORM])
    self.assertEqual(_A_CONFIG, args.config)
    self.assertEqual(_A_PLATFORM, args.platform)

  def testInconsistentEnvironmentSunnyDay(self):
    _SetEnvironBuildConfiguration(_A_CONFIG, _A_PLATFORM)
    arg_parser = _CreateParser()
    args = arg_parser.parse_args([])
    self.assertEqual(_A_CONFIG, args.config)
    self.assertEqual(_A_PLATFORM, args.platform)


if __name__ == '__main__':
  unittest.main()
