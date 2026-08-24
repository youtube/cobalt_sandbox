#!/usr/bin/env python3
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
"""Formats a collated JSON CI report into a human-readable Markdown table.

This script reads 'combined_report.json' and outputs 'combined_report.md'
with a clean status table.
"""

import json
import sys


def main() -> None:
  """Main function to format the CI report."""
  try:
    with open('combined_report.json', 'r', encoding='utf-8') as f:
      report_data = json.load(f)
  except FileNotFoundError:
    print('Error: combined_report.json not found.')
    sys.exit(1)

  markdown_lines = [
      '## Combined CI Status Report',
      '',
      '| Platform | Build | On-Host Tests | On-Device Tests |'
      ' Unit Test Failures | Status |',
      '|---|---|---|---|---|---|',
  ]

  for entry in report_data:
    if entry['status'] == 'in_progress':
      markdown_lines.append(
          f"| {entry['workflow']} | - | - | - | - | ⏳ PENDING |")
    elif 'error' in entry:
      markdown_lines.append(f"| {entry['workflow']} | - | - | - | - | ❌ FAIL"
                            f" ({entry['error']}) |")
    else:
      d = entry['data']
      status_icon = '❌ FAIL' if d['failed'] else '✅ PASS'

      # Format unit test summary
      failures = d.get('test_failures', {}).get('failing_tests', {})
      num_failed = sum(len(v) for v in failures.values())
      test_summary = (f'{num_failed} failed tests'
                      if num_failed > 0 else 'All passed')

      markdown_lines.append(
          f"| {d.get('platform')} | {d.get('build_result')} |"
          f" {d.get('on_host_test_result')} |"
          f" {d.get('on_device_test_result')} | {test_summary} |"
          f' {status_icon} |')

  with open('combined_report.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(markdown_lines))


if __name__ == '__main__':
  main()
