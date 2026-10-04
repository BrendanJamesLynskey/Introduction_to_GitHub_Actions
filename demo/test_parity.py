"""JS port agrees with Python. Skips when Node is missing, unless REQUIRE_NODE=1."""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from stats import mean


def test_js_mean_matches_python():
    node = shutil.which("node")
    if node is None:
        if os.environ.get("REQUIRE_NODE") == "1":
            pytest.fail("node not installed, and REQUIRE_NODE=1")
        pytest.skip("node not installed")
    xs = [0.1, 0.2, 0.3, 1e9]
    out = subprocess.run([node, Path(__file__).with_name("parity.js")], input=json.dumps(xs),
                         capture_output=True, text=True, check=True)
    assert json.loads(out.stdout) == mean(xs)
