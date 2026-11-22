#!/usr/bin/env python3
"""Runs deploy.sh and remove.sh from start to finish against a mock of AWS (moto), with no real account.

    python3 server/test_deploy.py

The scripts call the real aws command line, pointed at the mock. The one thing the mock cannot do is
answer on the function's public URL, so `curl` is replaced by a stand-in that unpacks the zip the script
just uploaded and runs that code with the key the script stored: what answers is the deployed function.
Checked: a first deploy and a redeploy from a clone (how KsanHub runs it), from a clone with uncommitted
changes, pasted into a shell, the way Windows behaves (no zip command, CR at line ends), with KsanHub's
deploy key (which may not touch IAM), and after remove.sh.
Skipped when moto (with its server) or the aws command line is missing.
"""
import json
import logging
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REAL_AWS = shutil.which("aws")
os.environ["MOTO_IAM_LOAD_MANAGED_POLICIES"] = "true"
try:
    from moto.server import ThreadedMotoServer
except ImportError:
    ThreadedMotoServer = None
if ThreadedMotoServer is None or REAL_AWS is None:
    print("skip  deploy checks (pip install awscli 'moto[server]')")
    sys.exit(0)

FAILS = []


def check(ok, what):
    print(("ok    " if ok else "FAIL  ") + what)
    if not ok:
        FAILS.append(what)


def sh(*args, cwd=None, env=None, stdin=None):
    r = subprocess.run(list(args), cwd=cwd, env=env, input=stdin, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


with socket.socket() as probe:
    probe.bind(("127.0.0.1", 0))
    PORT = probe.getsockname()[1]
ENDPOINT = "http://127.0.0.1:%d" % PORT
logging.getLogger("werkzeug").setLevel(logging.ERROR)
server = ThreadedMotoServer(port=PORT, verbose=False)
server.start()

work = tempfile.mkdtemp(prefix="ei-deploy-")
bin_dir = os.path.join(work, "bin")
os.makedirs(bin_dir)
capture = os.path.join(work, "uploaded.zip")

# aws: keeps a copy of the zip on its way up, can refuse chosen commands, can end its lines the way
# the Windows build does (CR LF), and talks to the mock.
with open(os.path.join(bin_dir, "aws"), "w") as fh:
    fh.write("""#!/usr/bin/env bash
for a in "$@"; do [ "$a" = "fileb://fn.zip" ] && cp fn.zip "$EI_CAPTURE"; done
if [ -n "${EI_REFUSE:-}" ] && [[ "$1 $2" == $EI_REFUSE ]]; then echo "An error occurred (AccessDenied) when calling $2" >&2; exit 254; fi
if [ -n "${EI_CR:-}" ]; then "%s" --endpoint-url "%s" "$@" | sed 's/$/\r/'; exit "${PIPESTATUS[0]}"; fi
exec "%s" --endpoint-url "%s" "$@"
""" % (REAL_AWS, ENDPOINT, REAL_AWS, ENDPOINT))

# zip and node: can be made to look missing.
for tool, switch in (("zip", "EI_NOZIP"), ("node", "EI_NONODE")):
    real = shutil.which(tool)
    with open(os.path.join(bin_dir, tool), "w") as fh:
        fh.write('#!/bin/sh\n[ -n "$%s" ] && exit 127\n%s\n' % (switch, 'exec "%s" "$@"' % real if real else "exit 127"))
    os.chmod(os.path.join(bin_dir, tool), 0o755)
HAVE_NODE = shutil.which("node") is not None

# curl: the uploaded code answers, with the key that the deploy stored on the function.
with open(os.path.join(bin_dir, "curl"), "w") as fh:
    fh.write("""#!%s
import json, os, subprocess, sys, tempfile, urllib.parse, zipfile
args = sys.argv[1:]
url = next(a for a in args if a.startswith("http"))
body = args[args.index("-d") + 1] if "-d" in args else None
where = tempfile.mkdtemp()
zipfile.ZipFile(os.environ["EI_CAPTURE"]).extractall(where)
os.environ["EI_KEY"] = subprocess.run(
    ["aws", "lambda", "get-function-configuration", "--function-name", "exit-interview-rooms",
     "--query", "Environment.Variables.EI_KEY", "--output", "text"], capture_output=True, text=True).stdout.strip()
sys.path.insert(0, where)
import lambda_function as room
if body is None:
    print(json.dumps(room.info(urllib.parse.urlparse(url).path)))
else:
    print(json.dumps(room.handle(json.loads(body), room.MemStore())))
""" % sys.executable)
# sleep: the waits are for real AWS to catch up; the mock is ready at once.
with open(os.path.join(bin_dir, "sleep"), "w") as fh:
    fh.write("#!/bin/sh\nexit 0\n")
for name in ("aws", "curl", "sleep"):
    os.chmod(os.path.join(bin_dir, name), 0o755)

ENV = dict(os.environ, PATH=bin_dir + os.pathsep + os.environ["PATH"], EI_CAPTURE=capture, HOME=work,
           AWS_ACCESS_KEY_ID="test", AWS_SECRET_ACCESS_KEY="test", AWS_REGION="ap-southeast-2", AWS_DEFAULT_REGION="ap-southeast-2",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
ENV.pop("AWS_PROFILE", None)
ENV.pop("EI_REGION", None)


def uploaded():
    with zipfile.ZipFile(capture) as z:
        return sorted(z.namelist()), json.loads(z.read("build.json"))


def address(out):
    lines = [x for x in out.splitlines() if x.startswith("https://") and "/k/" in x]
    return lines[-1] if lines else ""


# A clone with the files as they are now, committed: what KsanHub's build checks out.
clone = os.path.join(work, "clone")
os.makedirs(os.path.join(clone, "server"))
for name in ("deploy.sh", "remove.sh", "lambda_function.py", "make_deploy.py"):
    shutil.copy(os.path.join(HERE, name), os.path.join(clone, "server", name))
git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "init.defaultBranch=main"]
sh(*git, "init", "-q", cwd=clone, env=ENV)
sh(*git, "add", "-A", cwd=clone, env=ENV)
sh(*git, "commit", "-q", "-m", "x", cwd=clone, env=ENV)
tree = sh("git", "rev-parse", "HEAD:server", cwd=clone, env=ENV)[1].strip()

code, out = sh("bash", "server/deploy.sh", cwd=clone, env=ENV)
first = address(out)
check(code == 0 and first.endswith("/k/" + first.rsplit("/", 1)[-1]) and len(first.rsplit("/", 1)[-1]) == 24, "first deploy from a clone succeeds and prints the server URL")
check("KSANHUB_SITE_URL=" + first in out.splitlines(), "it tells KsanHub the same URL on a line of its own")
names, build = uploaded()
check(names == ["build.json", "lambda_function.py"], "the upload holds the code and build.json")
check(len(tree) == 40 and build.get("tree") == tree, "build.json names the committed server folder")
check(len(build.get("deployedAt", "")) == 20 and build["deployedAt"].endswith("Z"), "build.json carries the time of the deploy")
check("リージョン: ap-southeast-2" in out, "the region comes from the environment")

code, out = sh("bash", os.path.join(clone, "server", "deploy.sh"), cwd=work, env=ENV)
check(code == 0 and address(out) == first, "a second deploy (called by its full path, from elsewhere) keeps the URL and the key")
check(uploaded()[1].get("tree") == tree, "and still finds the clone it lives in")

with open(os.path.join(clone, "server", "lambda_function.py"), "a") as fh:
    fh.write("\n# local edit\n")
code, out = sh("bash", "server/deploy.sh", cwd=clone, env=ENV)
check(code == 0 and uploaded()[1].get("tree") == "" and "配置する版: 不明" in out, "uncommitted changes in server/ are deployed as an unknown version")
sh("git", "checkout", "-q", "--", "server", cwd=clone, env=ENV)

script = open(os.path.join(HERE, "deploy.sh"), encoding="utf-8").read()
code, out = sh("bash", "-i", cwd=clone, env=ENV, stdin=script)
check(address(out) == first and uploaded()[1].get("tree") == "", "pasted into a shell it deploys too, as an unknown version")
check(not any(x.startswith("KSANHUB_SITE_URL=") for x in out.splitlines()), "and leaves out the line meant for KsanHub")

if HAVE_NODE:
    code, out = sh("bash", "server/deploy.sh", cwd=clone, env=dict(ENV, EI_NOZIP="1", EI_CR="1"))
    check(code == 0 and address(out) == first and "\r" not in address(out), "the Windows way (no zip, CR at line ends) deploys to the same URL")
    with zipfile.ZipFile(capture) as z:
        sound = z.testzip() is None and all(i.external_attr >> 16 == 0o100644 and i.compress_type == zipfile.ZIP_DEFLATED
                                            and i.date_time == (1980, 1, 1, 0, 0, 0) for i in z.infolist())
        same = z.read("lambda_function.py") == open(os.path.join(HERE, "lambda_function.py"), "rb").read()
    check(sound and same and uploaded()[0] == ["build.json", "lambda_function.py"] and uploaded()[1].get("tree") == tree,
          "the zip that Node.js writes is sound, readable by the function, and carries the same code and version")
else:
    print("skip  the Windows way (no node here)")
code, out = sh("bash", "server/deploy.sh", cwd=clone, env=dict(ENV, EI_NOZIP="1", EI_NONODE="1"))
check(code == 0 and uploaded()[1].get("tree") == tree, "with neither zip nor Node.js, Python packs the code")

code, out = sh("bash", "server/deploy.sh", cwd=clone, env=dict(ENV, EI_REFUSE="iam *-role-policy"))
check(code == 0 and address(out) == first and "ロールの権限を書き直せません" in out, "a key that may not change the existing role still replaces the code")
code, out = sh("bash", "server/deploy.sh", cwd=clone, env=dict(ENV, EI_REFUSE="iam *"))
check(code == 0 and address(out) == first and "IAM を扱えません" in out and "KSANHUB_SITE_URL=" + first in out.splitlines(),
      "KsanHub's key (no IAM at all) replaces the code of a function that exists")
code, out = sh("bash", "server/deploy.sh", cwd=clone, env=dict(ENV, EI_REFUSE="lambda update-function-code"))
check(code != 0 and not any(x.startswith("KSANHUB_SITE_URL=") for x in out.splitlines()) and "できました" not in out, "a refused upload fails the deploy")

code, out = sh("bash", "server/remove.sh", cwd=clone, env=ENV)
check("消しました" in out and sh("aws", "lambda", "get-function", "--function-name", "exit-interview-rooms", env=ENV)[0] != 0
      and sh("aws", "dynamodb", "describe-table", "--table-name", "ExitInterviewRooms", env=ENV)[0] != 0
      and sh("aws", "iam", "get-role", "--role-name", "exit-interview-lambda", env=ENV)[0] != 0, "remove.sh takes everything away")
code, out = sh("bash", "server/deploy.sh", cwd=clone, env=dict(ENV, EI_REFUSE="iam *"))
check(code != 0 and "初めての配置だけ" in out and "できました" not in out and not any(x.startswith("KSANHUB_SITE_URL=") for x in out.splitlines()),
      "KsanHub's key cannot make the first deploy, and says what to do instead")
code, out = sh("bash", "server/deploy.sh", cwd=clone, env=dict(ENV, EI_REFUSE="iam *-role-policy"))
check(code != 0 and "できました" not in out, "a first deploy that cannot set up the role stops")
sh("bash", "server/remove.sh", cwd=clone, env=ENV)
code, out = sh("bash", "server/deploy.sh", cwd=clone, env=ENV)
again = address(out)
check(code == 0 and again and again.rsplit("/", 1)[-1] != first.rsplit("/", 1)[-1], "a deploy after removal makes a new key")

server.stop()
shutil.rmtree(work, ignore_errors=True)
print("ALL OK" if not FAILS else "%d FAILED" % len(FAILS))
sys.exit(1 if FAILS else 0)
