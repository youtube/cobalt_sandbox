#!/usr/bin/env python3
"""Mock GHA step helper script."""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET


def parse_args():
  parser = argparse.ArgumentParser(description='Mock GHA step.')
  parser.add_argument(
      '--job-name', required=True, help='Name of the job (for rule matching)')
  parser.add_argument(
      '--job-type',
      choices=['build', 'test'],
      required=True,
      help='Type of job')
  parser.add_argument(
      '--output-dir', required=True, help='Directory to write outputs/results')
  parser.add_argument(
      '--test-targets', help='JSON array of test targets/executables')
  return parser.parse_args()


def load_config():
  config_path = os.path.join(
      os.environ.get('GITHUB_WORKSPACE', '.'),
      '.github/config/mock_config.json')
  if os.path.exists(config_path):
    try:
      with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    except Exception as e:  # pylint: disable=broad-except
      print(f'Error reading mock config: {e}')
  return {}


def find_rule(config, job_name):
  rules = config.get('rules', [])
  for rule in rules:
    pattern = rule.get('job_pattern')
    if pattern and re.match(pattern, job_name):
      return rule
  return None


def generate_xml(filepath, suite_name, case_name, failure_msg=None):
  root = ET.Element('testsuites')
  testsuite = ET.SubElement(root, 'testsuite', name=suite_name)
  testcase = ET.SubElement(testsuite, 'testcase', name=case_name)
  if failure_msg:
    failure = ET.SubElement(testcase, 'failure', message=failure_msg)
    failure.text = 'Mocked failure details'

  tree = ET.ElementTree(root)
  os.makedirs(os.path.dirname(filepath), exist_ok=True)
  tree.write(filepath, encoding='utf-8', xml_declaration=True)
  print(f'Generated XML: {filepath}')


def main():
  args = parse_args()
  config = load_config()
  attempt = int(os.environ.get('GITHUB_RUN_ATTEMPT', 1))

  print(f'Mock step running for job: {args.job_name}, '
        f'type: {args.job_type}, attempt: {attempt}')

  rule = find_rule(config, args.job_name)
  should_fail = False
  failure_details = None

  if rule:
    fail_until = rule.get('fail_until_attempt', 0)
    if attempt <= fail_until:
      should_fail = True
      failure_details = rule.get('failure_details', {})
      print(
          f'Rule matched. Simulating FAILURE (fail_until_attempt: {fail_until})'
      )
    else:
      print(f'Rule matched but attempt {attempt} > '
            f'fail_until_attempt {fail_until}. Simulating SUCCESS.')
  else:
    print('No matching rule found. Simulating SUCCESS.')

  if args.job_type == 'build':
    os.makedirs(args.output_dir, exist_ok=True)
    if should_fail:
      print('Simulating build failure.')
      sys.exit(1)
    else:
      print('Simulating build success.')
      if 'android' in args.output_dir or 'aosp' in args.output_dir:
        apk_dir = os.path.join(args.output_dir, 'apks')
        os.makedirs(apk_dir, exist_ok=True)
        apk_path = os.path.join(apk_dir, 'Cobalt.apk')
        with open(apk_path, 'w', encoding='utf-8') as f:
          f.write('dummy apk content')
        print(f'Generated dummy APK: {apk_path}')
      sys.exit(0)

  elif args.job_type == 'test':
    os.makedirs(args.output_dir, exist_ok=True)

    # Parse test targets to know what files to generate.
    targets = []
    if args.test_targets:
      try:
        targets = json.loads(args.test_targets)
      except Exception as e:  # pylint: disable=broad-except
        print(f'Error parsing test targets: {e}')

    if not targets:
      # Fallback if no targets passed (e.g. browser tests)
      targets = ['mock_test']

    for target_path in targets:
      if isinstance(target_path, dict):
        target_path = target_path.get('target', '')
      filename = os.path.basename(target_path)
      # Handle targets with colons (e.g., base:base_unittests)
      filename = filename.split(':')[-1]
      # Remove extension if any (like .exe or run_ prefix)
      test_name = filename.split('.')[0]
      if test_name.startswith('run_'):
        test_name = test_name[4:]

      xml_filename = f'{test_name}_result.xml'
      # Special case for browser tests
      if test_name == 'cobalt_browsertests':
        xml_filename = 'cobalt_browsertests_result.xml'

      xml_path = os.path.join(args.output_dir, xml_filename)
      log_path = os.path.join(args.output_dir, f'{test_name}_log.txt')

      # Write dummy log
      with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f'Mocked log for {test_name}\n')

      if should_fail:
        msg = failure_details.get(
            'message',
            'Simulated failure') if failure_details else 'Simulated failure'
        suite = failure_details.get(
            'suite', 'MockSuite') if failure_details else 'MockSuite'
        case = failure_details.get(
            'case', 'MockCase') if failure_details else 'MockCase'
        generate_xml(xml_path, suite, case, msg)
      else:
        generate_xml(xml_path, 'MockSuite', 'MockCasePass')

    if should_fail:
      sys.exit(1)
    else:
      sys.exit(0)


if __name__ == '__main__':
  main()
