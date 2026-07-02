# -*- coding: utf-8 -*-
"""결정적 proof 게이트: pytest(도메인별 AC + 회귀)를 돌려 tmp/proof-results.json 산출.

contract.json 의 `proof` 가 가리키는 명령. exit 0 = 전 게이트 통과.
구현(server/contexts/*)과 tests/ 는 build 단계(03_build)에서 채운다.
"""
import json
import pathlib
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
TMP = ROOT / "tmp"


def _pytest_cmd():
    """동작하는 pytest 러너를 찾는다: 콘솔 스크립트 우선, 없으면 -m pytest."""
    exe = shutil.which("pytest")
    if exe:
        return [exe]
    return [sys.executable, "-m", "pytest"]


def main():
    TMP.mkdir(exist_ok=True)
    junit = TMP / "junit.xml"
    proc = subprocess.run(
        _pytest_cmd() + ["-q", "--no-header",
                         f"--junitxml={junit}", str(ROOT / "tests")],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")

    tests, passed, failed = [], 0, 0
    if junit.exists():
        root = ET.parse(junit).getroot()
        for tc in root.iter("testcase"):
            ok = tc.find("failure") is None and tc.find("error") is None
            tests.append({
                "name": tc.get("name"),
                "file": tc.get("classname"),
                "time_s": round(float(tc.get("time", 0)), 4),
                "status": "PASS" if ok else "FAIL",
            })
            passed += int(ok)
            failed += int(not ok)

    result = {
        "gate": "pytest",
        "feature": "cyworld (일촌·미니홈피·방명록·도토리 MVP)",
        "acceptance": ["chon", "minihomepy", "guestbook", "acorn", "회귀"],
        "exit_code": proc.returncode,
        "total": len(tests),
        "passed": passed,
        "failed": failed,
        "status": "PASS" if proc.returncode == 0 and failed == 0 else "FAIL",
        "tests": tests,
    }
    (TMP / "proof-results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out.rstrip())
    print(f"[proof] {result['status']} · {passed}/{len(tests)} passed "
          f"→ tmp/proof-results.json")
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
