# pylint: disable=missing-module-docstring,missing-class-docstring
from setuptools import setup
from setuptools.command.build_py import build_py
import subprocess
import sys
import os


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

    top_level_dir = os.path.abspath(os.path.dirname(__file__))
    os.environ['PYTHONPATH'] = top_level_dir

    print('Downloading the Chromium Clang toolchain.. ')
    run_command('starboard/tools/download_clang.sh')

    print('Generating build files with GN...')
    run_command([
        'gn', 'gen', 'out/linux-x64x11-egl_devel',
        ('--args=target_platform="linux-x64x11-egl"'
         'build_type="devel"'
         'enable_cc_wrapper=false')
    ])

    print('Building project with Ninja...')
    # Building a small binary that doesn't time out on public runners.
    run_command(['ninja', '-C', 'out/linux-x64x11-egl_devel','starboard_glclear_example'])


setup(
    name='Cobalt',
    version='25.0',
    packages=['cobalt'],
    cmdclass={'build_py': CustomBuild})
