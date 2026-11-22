"""Check the public talk's structure and numbers without model calls or Docker."""

import hashlib
import json
from pathlib import Path
import re
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PIN = "7cb5b3ee215287717edbb2cdf0ecb34f232a1c4c"
INPUT = "reports/plots/current_comparison.json"
EXPECTED_SHA = "ae5a1ff7569813b279175f989147f6508792de13122b643c44274a3ce98c4531"


def main():
    html = (HERE / "index.html").read_text()
    notes = (HERE / "speaker-notes.md").read_text()
    evidence = json.loads(re.search(
        r'<script id="evidence-data" type="application/json">(.*?)</script>',
        html, re.S,
    ).group(1))
    slides = re.findall(r'<section class="slide[^"]*" id="([^"]+)"', html)
    assert slides == [f"slide-{i}" for i in range(1, 11)] + ["appendix-a", "appendix-b"]
    assert sum(map(float, re.findall(r'data-minutes="([\d.]+)"', html))) == 23
    assert not re.search(r'\bsrc\s*=\s*["\']https?://|@import|url\(https?://', html)
    assert "fetch(" not in html, "Opening a local file must not need fetch or a server"
    for href in re.findall(r'href="#([^"]+)"', html):
        assert f'id="{href}"' in html

    raw = subprocess.check_output(["git", "show", f"{PIN}:{INPUT}"], cwd=ROOT)
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA
    points = json.loads(raw)["points"]
    for variant in ("baseline", "ponytail"):
        point, = [p for p in points if p["variant"] == variant and p["step"] == 6]
        assert point["n_trajectories"] == 2
        for key, values in evidence["benchmark"][variant].items():
            for stat, value in values.items():
                assert value == point["metrics"][key][stat], (variant, key, stat)
    baseline, ponytail = evidence["benchmark"]["baseline"], evidence["benchmark"]["ponytail"]
    for other in evidence["otherTrajectories"]:
        point, = [p for p in points if p["variant"] == other["variant"] and p["step"] == 6]
        assert other["n"] == point["n_trajectories"]
        assert other["setupFingerprint"] == point["setup_fingerprint"]
        for key in ("net_prod_loc", "output_tokens", "sonar_delta_cognitive_complexity"):
            assert other[key] == point["metrics"][key]["mean"]
    for key, label in (("net_prod_loc", "27.2%"), ("output_tokens", "6.8%")):
        reduction = (1 - ponytail[key]["mean"] / baseline[key]["mean"]) * 100
        assert f"{reduction:.1f}%" == label and label in html

    script = notes.split("## 1.", 1)[1].split("## Q&A", 1)[0]
    script = re.sub(r"\[[^\]]*\]|^## .*", "", script, flags=re.M)
    words = len(re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b", script))
    assert 2200 <= words <= 2500, words
    bio = re.search(r"^> (Artem Demidov.*)$", notes, re.M).group(1)
    assert 55 <= len(bio.split()) <= 60
    assert (HERE / "deck.pdf").read_bytes().startswith(b"%PDF-")
    print(f"PASS: 10 main + 2 appendix slides; 23 scheduled minutes; {words} script words; {len(bio.split())}-word bio")
    print("PASS: benchmark values match pinned public input; rounded differences match")
    print("Scope: public analysis/structure only. Browser, PDF pages and human rehearsal are separate checks.")


if __name__ == "__main__":
    main()
