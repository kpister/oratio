import os
import sys

# Used to determine where in the repo we are.
path = os.getcwd().split("/")
assert "oratio" in path
ret = []

for folder in path:
    ret.append(folder)
    if folder == "oratio":
        break

sys.path.append(os.path.join("/".join(ret), "src"))
