import os

os.environ["PIPENV_IGNORE_VIRTUALENVS"] = "1"

cmds = ["flake8", "mypy"]
for cmd in cmds:
    print(cmd)
    os.system(f"pipenv run {cmd}")
    print()
