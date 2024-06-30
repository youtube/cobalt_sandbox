# pylint: disable=missing-module-docstring,missing-class-docstring
from setuptools import setup
from setuptools.command.build_py import build_py
import subprocess
import sys


def run_command(command, cwd=None):
  """Utility function to run a shell command and stream its output."""
  try:
    with subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1) as process:
      # Stream output in real-time
      for line in process.stdout:
        print(line, end='')  # end='' to avoid double newlines
      process.stdout.close()
      return_code = process.wait()
      if return_code:
        raise subprocess.CalledProcessError(return_code, command)
  except subprocess.CalledProcessError as e:
    print('Command failed with return code', e.returncode)
    sys.exit(1)


class CustomBuild(build_py):

  def run(self):
    super().run()

    # Running GN to generate build files
    print('Generating build files with GN...')
    run_command(
        ['python', 'cobalt/build/gn.py', '-p', 'linux-x64x11', '-C', 'devel'])

    # Running Ninja to build the project
    print('Building project with Ninja...')
    run_command(['ninja', '-C', 'out/linux-x64x11_devel'])


setup(
    name='Cobalt',
    version='25.0',
    packages=['cobalt'],
    cmdclass={'build_py': CustomBuild})
