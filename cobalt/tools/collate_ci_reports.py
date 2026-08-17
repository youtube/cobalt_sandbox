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
"""Collates CI report fragments from different workflow runs of the same commit.

This script queries the GitHub API to find all active and completed workflow
runs for a given commit, downloads their validation report fragments, and
aggregates them into a single JSON report.
"""

import argparse
import glob
import json
import os
import subprocess
import sys


def run_cmd(cmd: list[str]) -> str:
  """Runs a shell command and returns its stdout.

  Args:
    cmd: A list of command arguments.

  Returns:
    The stdout of the command.
  """
  res = subprocess.run(cmd, capture_output=True, text=True, check=True)
  return res.stdout


def main() -> None:
  """Main function to collate CI reports."""
  parser = argparse.ArgumentParser(
      description='Collate CI reports for a commit.')
  parser.add_argument(
      '--sha', required=True, help='The commit SHA to check runs for.')
  args = parser.parse_args()

  # Get all runs for the commit
  runs_json = run_cmd([
      'gh',
      'run',
      'list',
      '--commit',
      args.sha,
      '--json',
      'databaseId,workflowName,status,conclusion',
  ])
  # Sort runs by databaseId descending to ensure we process the newest first.
  runs = sorted(
      json.loads(runs_json), key=lambda x: x['databaseId'], reverse=True)

  # We only care about the workflows that run main.yaml
  target_workflows = {'android', 'aosp', 'evergreen', 'linux'}
  seen_workflows = set()
  ci_runs = []
  for r in runs:
    wf_name = r['workflowName']
    if wf_name in target_workflows and wf_name not in seen_workflows:
      ci_runs.append(r)
      seen_workflows.add(wf_name)

  os.makedirs('fragments', exist_ok=True)
  report_data = []
  any_pending = False
  overall_failed = False

  # Check for missing workflows that haven't registered yet.
  missing_workflows = target_workflows - seen_workflows
  if missing_workflows:
    any_pending = True
    for wf in missing_workflows:
      report_data.append({
          'workflow': wf,
          'status': 'in_progress',
          'platforms': []
      })

  for run in ci_runs:
    run_id = str(run['databaseId'])
    wf_name = run['workflowName']
    status = run['status']
    conclusion = run['conclusion']

    if status != 'completed':
      any_pending = True
      report_data.append({
          'workflow': wf_name,
          'status': 'in_progress',
          'platforms': []
      })
      continue

    if conclusion != 'success':
      overall_failed = True

    run_cmd([
        'gh',
        'run',
        'download',
        run_id,
        '--pattern',
        'validation-report-*',
        '--dir',
        'fragments',
    ])

  # Read downloaded fragments
  fragment_files = glob.glob('fragments/**/*.json', recursive=True)
  for f_path in fragment_files:
    with open(f_path, 'r', encoding='utf-8') as f:
      data = json.load(f)
      report_data.append({
          'workflow': data.get('platform', 'Unknown'),
          'status': 'completed',
          'data': data,
      })
      if data.get('failed'):
        overall_failed = True

  with open('combined_report.json', 'w', encoding='utf-8') as f:
    json.dump(report_data, f, indent=2)

  # Determine status and exit
  if any_pending:
    print('STATUS: PENDING')
    sys.exit(0)
  elif overall_failed:
    print('STATUS: FAILURE')
    sys.exit(1)
  else:
    print('STATUS: SUCCESS')
    sys.exit(0)


if __name__ == '__main__':
  main()
