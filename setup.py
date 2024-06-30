# pylint: disable=missing-module-docstring
from setuptools import setup
from setuptools.command.build_py import build_py


class CustomBuild(build_py):

  def run(self):
    # Place your custom build logic here
    print('Running custom build steps')
    super().run()


setup(
    name='Cobalt',
    version='25.0',
    packages=['cobalt-runtime'],
    cmdclass={'build_py': CustomBuild})
