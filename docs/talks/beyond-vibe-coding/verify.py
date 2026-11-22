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
    assert slides == [f"slide-{i}" for i in range(1, 27)] + ["appendix-a", "appendix-b"]
    assert abs(sum(map(float, re.findall(r'data-minutes="([\d.]+)"', html))) - 23) < 1e-9
    assert not re.search(r'\bsrc\s*=\s*["\']https?://|@import|url\(https?://', html)
    assert "fetch(" not in html, "Opening a local file must not need fetch or a server"
    for href in re.findall(r'href="#([^"]+)"', html):
        assert f'id="{href}"' in html
    for image in re.findall(r'<img[^>]*\bsrc="([^"]+)"', html):
        assert image.startswith("assets/") and (HERE / image).is_file(), image
    main_html = html.split('<section class="slide appendix"', 1)[0]
    cover = main_html.split('id="slide-2"', 1)[0]
    assert "Personal experience" not in cover and "Use selected month" not in main_html
    assert "7/8" not in main_html and "unresolved" not in main_html
    assert 'id="slide-4"' in main_html and ">Agenda<" in main_html
    assert "Use Planning Mode." in main_html
    assert "red-box" in html and "red-underline" in html
    assert "Nearly full" in html and "Room to continue" in html
    assert "95%" not in main_html and "Do not implement yet" not in main_html
    assert 'class="context-meter crowded"' in main_html
    assert "Set the finish line with /goal" in main_html
    assert "saved plan + /goal" in main_html
    assert "Save plan + set /goal" in main_html
    assert "planning-chat.png" not in html and "save-chat.png" not in html
    assert "An independent check: JetBrains" in main_html
    assert "Keep your setup simple" in main_html
    for link in (
        'https://learn.chatgpt.com/guides/best-practices',
        'https://code.claude.com/docs/en/common-workflows#plan-before-editing',
        'https://code.claude.com/docs/en/best-practices#give-claude-a-check-to-run',
    ):
        assert f'<a href="{link}">' in main_html

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
    for key, label in (("net_prod_loc", "≈27%"), ("output_tokens", "≈7%")):
        reduction = (1 - ponytail[key]["mean"] / baseline[key]["mean"]) * 100
        assert f"≈{reduction:.0f}%" == label and label in main_html

    caveman, = [t for t in evidence["otherTrajectories"] if t["variant"] == "caveman"]
    output_increase = 100 * (caveman["output_tokens"] / baseline["output_tokens"]["mean"] - 1)
    assert f"≈{output_increase:.0f}% more" == "≈28% more" and "≈28% more" in main_html
    claude, codex = evidence["models"]
    assert round(claude["meanApiCostUsd"] / codex["meanApiCostUsd"]) == 13
    assert round(100 * (1 - codex["index"] / claude["index"])) == 12
    assert "≈13× lower cost" in main_html and "≈12% lower index" in main_html
    independent = evidence["independent"]
    assert round(independent["ponytail"]["codeReductionPercent"]) == 15
    assert round(independent["ponytail"]["costReductionPercent"]) == 10
    # Display half percentages with conventional half-up rounding.
    assert int(independent["caveman"]["outputReductionPercent"] + .5) == 9
    assert evidence["ecc"]["steps"] == 6 and evidence["ecc"]["trajectories"] == 1
    ecc_results = subprocess.check_output(["git", "show", f"{PIN}:reports/ecc_results.md"], cwd=ROOT).decode()
    assert "123,655 output tokens" in ecc_results
    assert "net production growth is 468 lines" in ecc_results
    assert evidence["ecc"]["outputTokens"] == 123655 and evidence["ecc"]["netProdLoc"] == 468

    script = notes.split("## 1.", 1)[1].split("## Appendix reference", 1)[0]
    script = re.sub(r"\[[^\]]*\]|^## .*", "", script, flags=re.M)
    words = len(re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b", script))
    bio = re.search(r"^> (Artem Demidov.*)$", notes, re.M).group(1)
    assert 55 <= len(bio.split()) <= 60
    assert (HERE / "deck.pdf").read_bytes().startswith(b"%PDF-")
    print(f"PASS: 26 main frames + 2 appendices; 23 scheduled minutes; {words} script words; {len(bio.split())}-word bio")
    print("PASS: benchmark values match pinned public input; rounded differences match")
    print("Scope: public analysis/assets/structure. Browser and PDF review are separate. Live rehearsal is not a delivery gate.")


if __name__ == "__main__":
    main()
