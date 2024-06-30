# pylint: disable=missing-module-docstring,invalid-name


def configure(_ctx):
  pass


def build(ctx):
  ctx.exec_command('echo Hello, Waf for CODEQL !')
