# Copyright 2026 The Cobalt Authors. All Rights Reserved.
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
"""Tests for collate_ci_reports.py and format_ci_report.py."""

import io
import json
import os
import shutil
import unittest
from unittest.mock import patch, MagicMock

# Import the main functions.
from cobalt.tools.collate_ci_reports import main as collate_main
from cobalt.tools.format_ci_report import main as format_main


class TestCollateAndFormatCiReports(unittest.TestCase):
  """Test cases for CI report collation and formatting."""

  def setUp(self) -> None:
    """Set up test environment and clean up previous run files."""
    self.cleanup_files = [
        'combined_report.md',
        'combined_report.json',
        'fragments',
        'status.txt',
    ]
    self.cleanup()

  def tearDown(self) -> None:
    """Clean up files after tests."""
    self.cleanup()

  def cleanup(self) -> None:
    """Helper to remove temporary files."""
    for f in self.cleanup_files:
      if os.path.exists(f):
        if os.path.isdir(f):
          shutil.rmtree(f)
        else:
          os.remove(f)

  @patch('cobalt.tools.collate_ci_reports.run_cmd')
  @patch('sys.stdout', new_callable=io.StringIO)
  def test_collate_and_format_success(self, mock_stdout: io.StringIO,
                                      mock_run_cmd: MagicMock) -> None:
    """Tests successful collation and formatting of reports."""
    # Mock gh run list
    mock_runs = [
        {
            'databaseId': 111,
            'workflowName': 'linux',
            'status': 'completed',
            'conclusion': 'success',
        },
        {
            'databaseId': 222,
            'workflowName': 'android',
            'status': 'completed',
            'conclusion': 'success',
        },
        {
            'databaseId': 333,
            'workflowName': 'aosp',
            'status': 'completed',
            'conclusion': 'success',
        },
        {
            'databaseId': 444,
            'workflowName': 'evergreen',
            'status': 'completed',
            'conclusion': 'success',
        },
    ]

    def side_effect(cmd: list[str]) -> str:
      if 'list' in cmd:
        return json.dumps(mock_runs)
      elif 'download' in cmd:
        run_id = cmd[3]
        os.makedirs('fragments', exist_ok=True)
        if run_id == '111':
          with open(
              'fragments/report_linux-x64.json', 'w', encoding='utf-8') as f:
            json.dump(
                {
                    'platform': 'linux-x64x11',
                    'config': 'devel',
                    'build_result': 'success',
                    'on_device_test_result': 'success',
                    'on_host_test_result': 'success',
                    'web_tests_result': 'success',
                    'test_failures': {},
                    'failed': False,
                },
                f,
            )
        elif run_id == '222':
          with open(
              'fragments/report_android-arm64.json', 'w',
              encoding='utf-8') as f:
            json.dump(
                {
                    'platform': 'android-arm64',
                    'config': 'devel',
                    'build_result': 'success',
                    'on_device_test_result': 'success',
                    'on_host_test_result': 'success',
                    'web_tests_result': 'success',
                    'test_failures': {},
                    'failed': False,
                },
                f,
            )
        elif run_id == '333':
          with open('fragments/report_aosp.json', 'w', encoding='utf-8') as f:
            json.dump(
                {
                    'platform': 'aosp-x86',
                    'config': 'devel',
                    'build_result': 'success',
                    'failed': False,
                },
                f,
            )
        elif run_id == '444':
          with open(
              'fragments/report_evergreen.json', 'w', encoding='utf-8') as f:
            json.dump(
                {
                    'platform': 'evergreen-x64',
                    'config': 'devel',
                    'build_result': 'success',
                    'failed': False,
                },
                f,
            )
        return ''
      return ''

    mock_run_cmd.side_effect = side_effect

    with patch('sys.argv', ['collate_ci_reports.py', '--sha', 'dummy_sha']):
      with self.assertRaises(SystemExit) as cm:
        collate_main()

      # Should exit with 0
      self.assertEqual(cm.exception.code, 0)
      self.assertIn('STATUS: SUCCESS', mock_stdout.getvalue())

    # Check combined_report.json
    self.assertTrue(os.path.exists('combined_report.json'))

    # Run formatter
    format_main()

    # Check combined_report.md
    self.assertTrue(os.path.exists('combined_report.md'))
    with open('combined_report.md', 'r', encoding='utf-8') as f:
      md = f.read()
      self.assertIn('linux-x64x11', md)
      self.assertIn('android-arm64', md)
      self.assertIn('✅ PASS', md)

  @patch('cobalt.tools.collate_ci_reports.run_cmd')
  @patch('sys.stdout', new_callable=io.StringIO)
  def test_collate_and_format_failure(self, mock_stdout: io.StringIO,
                                      mock_run_cmd: MagicMock) -> None:
    """Tests collation and formatting when there is a CI failure."""
    # Mock runs where one has failed
    mock_runs = [
        {
            'databaseId': 111,
            'workflowName': 'linux',
            'status': 'completed',
            'conclusion': 'failure',
        },
        {
            'databaseId': 222,
            'workflowName': 'android',
            'status': 'completed',
            'conclusion': 'success',
        },
        {
            'databaseId': 333,
            'workflowName': 'aosp',
            'status': 'completed',
            'conclusion': 'success',
        },
        {
            'databaseId': 444,
            'workflowName': 'evergreen',
            'status': 'completed',
            'conclusion': 'success',
        },
    ]

    def side_effect(cmd: list[str]) -> str:
      if 'list' in cmd:
        return json.dumps(mock_runs)
      elif 'download' in cmd:
        run_id = cmd[3]
        os.makedirs('fragments', exist_ok=True)
        if run_id == '111':
          with open(
              'fragments/report_linux-x64.json', 'w', encoding='utf-8') as f:
            json.dump(
                {
                    'platform': 'linux-x64x11',
                    'config': 'devel',
                    'build_result': 'success',
                    'on_device_test_result': 'failure',
                    'on_host_test_result': 'success',
                    'web_tests_result': 'success',
                    'test_failures': {
                        'failing_tests': {
                            'results/starboard_platform_tests.xml': [{
                                'name': 'TestSuite.TestName',
                                'message': 'Failed',
                            }]
                        }
                    },
                    'failed': True,
                },
                f,
            )
        elif run_id == '222':
          with open(
              'fragments/report_android-arm64.json', 'w',
              encoding='utf-8') as f:
            json.dump(
                {
                    'platform': 'android-arm64',
                    'config': 'devel',
                    'build_result': 'success',
                    'on_device_test_result': 'success',
                    'on_host_test_result': 'success',
                    'web_tests_result': 'success',
                    'test_failures': {},
                    'failed': False,
                },
                f,
            )
        elif run_id == '333':
          with open('fragments/report_aosp.json', 'w', encoding='utf-8') as f:
            json.dump(
                {
                    'platform': 'aosp-x86',
                    'config': 'devel',
                    'build_result': 'success',
                    'failed': False,
                },
                f,
            )
        elif run_id == '444':
          with open(
              'fragments/report_evergreen.json', 'w', encoding='utf-8') as f:
            json.dump(
                {
                    'platform': 'evergreen-x64',
                    'config': 'devel',
                    'build_result': 'success',
                    'failed': False,
                },
                f,
            )
        return ''
      return ''

    mock_run_cmd.side_effect = side_effect

    with patch('sys.argv', ['collate_ci_reports.py', '--sha', 'dummy_sha']):
      with self.assertRaises(SystemExit) as cm:
        collate_main()

      # Should exit with 1 (failure)
      self.assertEqual(cm.exception.code, 1)
      self.assertIn('STATUS: FAILURE', mock_stdout.getvalue())

    # Run formatter
    format_main()

    with open('combined_report.md', 'r', encoding='utf-8') as f:
      md = f.read()
      self.assertIn('linux-x64x11', md)
      self.assertIn('1 failed tests', md)
      self.assertIn('❌ FAIL', md)

  @patch('cobalt.tools.collate_ci_reports.run_cmd')
  @patch('sys.stdout', new_callable=io.StringIO)
  def test_collate_and_format_pending(self, mock_stdout: io.StringIO,
                                      mock_run_cmd: MagicMock) -> None:
    """Tests collation and formatting when some runs are still pending."""
    # One run completed success, one is still in progress
    mock_runs = [
        {
            'databaseId': 111,
            'workflowName': 'linux',
            'status': 'completed',
            'conclusion': 'success',
        },
        {
            'databaseId': 222,
            'workflowName': 'android',
            'status': 'in_progress',
            'conclusion': None,
        },
    ]

    def side_effect(cmd: list[str]) -> str:
      if 'list' in cmd:
        return json.dumps(mock_runs)
      elif 'download' in cmd:
        run_id = cmd[3]
        os.makedirs('fragments', exist_ok=True)
        if run_id == '111':
          with open(
              'fragments/report_linux-x64.json', 'w', encoding='utf-8') as f:
            json.dump(
                {
                    'platform': 'linux-x64x11',
                    'config': 'devel',
                    'build_result': 'success',
                    'on_device_test_result': 'success',
                    'on_host_test_result': 'success',
                    'failed': False,
                },
                f,
            )
        return ''
      return ''

    mock_run_cmd.side_effect = side_effect

    with patch('sys.argv', ['collate_ci_reports.py', '--sha', 'dummy_sha']):
      with self.assertRaises(SystemExit) as cm:
        collate_main()

      self.assertEqual(cm.exception.code, 0)
      self.assertIn('STATUS: PENDING', mock_stdout.getvalue())

    # Run formatter
    format_main()

    with open('combined_report.md', 'r', encoding='utf-8') as f:
      md = f.read()
      self.assertIn('android', md)
      self.assertIn('⏳ PENDING', md)

  @patch('cobalt.tools.collate_ci_reports.run_cmd')
  @patch('sys.stdout', new_callable=io.StringIO)
  def test_collate_duplicate_runs(self, mock_stdout: io.StringIO,
                                  mock_run_cmd: MagicMock) -> None:
    """Tests that only the latest run for each workflow name is collated."""
    # Mock runs where 'linux' has an old failed run and a new successful run.
    mock_runs = [
        {
            'databaseId': 222,  # Latest run
            'workflowName': 'linux',
            'status': 'completed',
            'conclusion': 'success',
        },
        {
            'databaseId': 111,  # Older run
            'workflowName': 'linux',
            'status': 'completed',
            'conclusion': 'failure',
        },
        {
            'databaseId': 333,
            'workflowName': 'android',
            'status': 'completed',
            'conclusion': 'success',
        },
        {
            'databaseId': 444,
            'workflowName': 'aosp',
            'status': 'completed',
            'conclusion': 'success',
        },
        {
            'databaseId': 555,
            'workflowName': 'evergreen',
            'status': 'completed',
            'conclusion': 'success',
        },
    ]

    def side_effect(cmd: list[str]) -> str:
      if 'list' in cmd:
        return json.dumps(mock_runs)
      elif 'download' in cmd:
        run_id = cmd[3]
        os.makedirs('fragments', exist_ok=True)
        if run_id == '222':
          with open(
              'fragments/report_linux-x64_new.json', 'w',
              encoding='utf-8') as f:
            json.dump(
                {
                    'platform': 'linux-x64x11',
                    'config': 'devel',
                    'build_result': 'success',
                    'failed': False,
                },
                f,
            )
        elif run_id == '111':
          self.fail('Downloaded artifacts from an older run.')
        elif run_id == '333':
          with open(
              'fragments/report_android.json', 'w', encoding='utf-8') as f:
            json.dump(
                {
                    'platform': 'android-arm64',
                    'config': 'devel',
                    'build_result': 'success',
                    'failed': False,
                },
                f,
            )
        elif run_id == '444':
          with open('fragments/report_aosp.json', 'w', encoding='utf-8') as f:
            json.dump(
                {
                    'platform': 'aosp-x86',
                    'config': 'devel',
                    'build_result': 'success',
                    'failed': False,
                },
                f,
            )
        elif run_id == '555':
          with open(
              'fragments/report_evergreen.json', 'w', encoding='utf-8') as f:
            json.dump(
                {
                    'platform': 'evergreen-x64',
                    'config': 'devel',
                    'build_result': 'success',
                    'failed': False,
                },
                f,
            )
        return ''
      return ''

    mock_run_cmd.side_effect = side_effect

    with patch('sys.argv', ['collate_ci_reports.py', '--sha', 'dummy_sha']):
      with self.assertRaises(SystemExit) as cm:
        collate_main()

      self.assertEqual(cm.exception.code, 0)
      self.assertIn('STATUS: SUCCESS', mock_stdout.getvalue())

    format_main()
    with open('combined_report.md', 'r', encoding='utf-8') as f:
      md = f.read()
      self.assertIn('linux-x64x11', md)
      self.assertIn('✅ PASS', md)

  @patch('cobalt.tools.collate_ci_reports.run_cmd')
  @patch('sys.stdout', new_callable=io.StringIO)
  def test_collate_missing_workflows(self, mock_stdout: io.StringIO,
                                     mock_run_cmd: MagicMock) -> None:
    """Tests that missing target workflows are marked as pending."""
    # Mock runs has only 'linux'; others ('android', etc.) are missing.
    mock_runs = [{
        'databaseId': 111,
        'workflowName': 'linux',
        'status': 'completed',
        'conclusion': 'success',
    }]

    def side_effect(cmd: list[str]) -> str:
      if 'list' in cmd:
        return json.dumps(mock_runs)
      elif 'download' in cmd:
        os.makedirs('fragments', exist_ok=True)
        with open('fragments/report_linux.json', 'w', encoding='utf-8') as f:
          json.dump(
              {
                  'platform': 'linux-x64x11',
                  'config': 'devel',
                  'build_result': 'success',
                  'failed': False,
              },
              f,
          )
        return ''
      return ''

    mock_run_cmd.side_effect = side_effect

    with patch('sys.argv', ['collate_ci_reports.py', '--sha', 'dummy_sha']):
      with self.assertRaises(SystemExit) as cm:
        collate_main()

      self.assertEqual(cm.exception.code, 0)
      self.assertIn('STATUS: PENDING', mock_stdout.getvalue())

    format_main()
    with open('combined_report.md', 'r', encoding='utf-8') as f:
      md = f.read()
      # Linux is success
      self.assertIn('linux-x64x11', md)
      self.assertIn('✅ PASS', md)
      # Missing workflows (like android) are pending
      self.assertIn('android', md)
      self.assertIn('⏳ PENDING', md)


if __name__ == '__main__':
  unittest.main()
