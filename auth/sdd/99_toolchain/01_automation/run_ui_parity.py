# -*- coding: utf-8 -*-
"""UI parity 게이트 — OTP 화면 렌더를 스냅샷과 대조한다.

강의 데모의 Playwright exactness gate를 이 환경(브라우저 비가용)에서
결정적 HTML 스냅샷 parity로 대체. exit 0 = 일치.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from server.contexts.auth import screens  # noqa: E402

SNAP = ROOT / "sdd/04_verify/10_test/ui_parity/signup_otp.html"


def main():
    want = SNAP.read_text(encoding="utf-8").strip()
    got = screens.render("signup_otp").strip()
    ok = want == got
    print("화면: signup_otp")
    print(f"스냅샷: {SNAP.relative_to(ROOT)}")
    print("UI parity (스냅샷 대조):", "일치" if ok else "불일치")
    print(f"RESULT: ui_parity {'1/1' if ok else '0/1'}  ·  {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
