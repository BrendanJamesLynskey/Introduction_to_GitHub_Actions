"""Stand-in for an expensive step whose output is worth caching (a downloaded dataset, a built tool)."""
import json
import random
import sys
from pathlib import Path

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
rng = random.Random(42)
(out / "samples.json").write_text(json.dumps([rng.random() for _ in range(1000)]))
print("built", out / "samples.json")
