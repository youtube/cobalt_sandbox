#!/usr/bin/env python3
#
# Copyright 2022 The Cobalt Authors. All Rights Reserved.
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
"""gRPC On-device Tests Gateway client."""

import argparse
import logging
import sys

import grpc

import on_device_tests_gateway_pb2
import on_device_tests_gateway_pb2_grpc


# All tests On-Device tests support
_TEST_TYPES = [
    'unit_test',
    'black_box_test',
    'evergreen_test',
    'performance_test',
    'endurance_test',
    'integration_test',
    'upload_archive',
]

# All platforms On-Device tests support
_PLATFORM_TYPES = [
    'android-arm',
    'android-arm64',
    'android-x86',
    'raspi-2',
]

# All test configs On-Device tests support
_TEST_CONFIGS = [
  'devel',
  'staging',
  'production',
]


_WORK_DIR = '/on_device_tests_gateway'
_ON_DEVICE_TESTS_GATEWAY_SERVICE_HOST = 'on-device-tests-gateway-service'
_ON_DEVICE_TESTS_GATEWAY_SERVICE_PORT = '50052'


class OnDeviceTestsGatewayClient():
  """On-device tests Gateway Client class."""

  def __init__(self):
    self.channel = grpc.insecure_channel(
      target='%s:%s' %
        (_ON_DEVICE_TESTS_GATEWAY_SERVICE_HOST,
         _ON_DEVICE_TESTS_GATEWAY_SERVICE_PORT),
      # These options need to match server settings.
      options=[
        ('grpc.keepalive_time_ms', 10000),
        ('grpc.keepalive_timeout_ms', 5000),
        ('grpc.keepalive_permit_without_calls', 1),
        ('grpc.http2.max_pings_without_data', 0),
        ('grpc.http2.min_time_between_pings_ms', 10000),
        ('grpc.http2.min_ping_interval_without_data_ms', 5000)
      ]
    )
    self.stub = on_device_tests_gateway_pb2_grpc.on_device_tests_gatewayStub(
        self.channel)

  def run_command(self, workdir, args):
    for response_line in self.stub.exec_command(
        on_device_tests_gateway_pb2.OnDeviceTestsCommand(
          workdir=workdir,
          token=args.token,
          test_type=args.test_type,
          platform=args.platform,
          archive_path=args.archive_path,
          config=args.config,
          tag=args.tag,
          label=args.label,
          builder_name=args.builder_name,
          change_id=args.change_id,
          build_number=args.build_number,
        )):

      print(response_line.response)


def main():
  """Main routine."""
  logging.basicConfig(
    level=logging.INFO,
    format='[%(filename)s:%(lineno)s] %(message)s'
  )

  parser = argparse.ArgumentParser(
    epilog=(
      'Example: ./on_device_tests_gateway_client.py '
      '--test_type=unit_test '
      '--remote_archive_path=gs://my_bucket/path/to/artifacts.tar '
      '--platform=raspi-2 '
      '--config=devel'
    ),
    formatter_class=argparse.RawDescriptionHelpFormatter
  )

  parser.add_argument(
    '-t', '--token',
    type=str,
    required=True,
    help='On Device Tests authentication token'
  )
  parser.add_argument(
    '-e', '--test_type',
    type=str,
    choices=_TEST_TYPES,
    required=True,
    help=f'Type of test to run.'
  )
  parser.add_argument(
    '-p', '--platform',
    type=str,
    choices=_PLATFORM_TYPES,
    required=True,
    help=f'Platform this test was built for.'
  )
  parser.add_argument(
    '-c', '--config',
    type=str,
    choices=_TEST_CONFIGS,
    required=True,
    help=f'Cobalt config being tested.'
  )
  parser.add_argument(
    '-a', '--archive_path',
    type=str,
    required=True,
    help='Path to Cobalt archive to be tested. Must be on gcs.'
  )
  parser.add_argument(
    '-g', '--tag',
    type=str,
    help='Value saved with performance results. '
      'Indicates why this test was triggered.'
  )
  parser.add_argument(
    '-l', '--label',
    type=str,
    help='Additional labels to assign to the test.'
  )
  parser.add_argument(
    '-b', '--builder_name',
    type=str,
    help='Name of the builder that built the artifacts, '
      'if any. Saved with performance test results'
  )
  parser.add_argument(
    '-i', '--change_id',
    type=str,
    help='ChangeId that triggered this test, if any. '
      'Saved with performance test results.'
  )
  parser.add_argument(
    '-n', '--build_number',
    type=str,
    help='Build number associated with the build, if any. '
      'Saved with performance test results.'
  )

  args = parser.parse_args()

  client = OnDeviceTestsGatewayClient()
  try:
    client.run_command(workdir=_WORK_DIR, args=args)
  except grpc.RpcError as e:
    print(e)
    return e.code().value


if __name__ == '__main__':
  sys.exit(main())
