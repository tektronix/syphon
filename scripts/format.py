import os

os.environ["PIPENV_IGNORE_VIRTUALENVS"] = "1"

cmds = ["isort", "black syphon tests setup.py"]
for cmd in cmds:
    print(cmd)
    os.system(f"pipenv run {cmd}")
    print()
