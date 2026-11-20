import sqlite3
import subprocess

API_KEY = "sk-live-secret-12345"


def add(x, items=[]):
  items.append(x)
  return items


def run_unsafe(user_input, cmd, uid):
  result = eval(user_input)
  subprocess.run(cmd, shell=True)
  conn = sqlite3.connect(":memory:")
  try:
    conn.execute(f"SELECT * FROM users WHERE id = {uid}")
  except:
    pass
  return result
