# -*- coding: utf-8 -*-
"""UI parity — OTP 화면 렌더가 스냅샷과 일치 (Playwright exactness 대용)."""
import pathlib

from server.contexts.auth import screens

SNAP = (pathlib.Path(__file__).resolve().parents[1]
        / "sdd/04_verify/10_test/ui_parity/signup_otp.html")


def test_signup_screen_parity():
    want = SNAP.read_text(encoding="utf-8").strip()
    got = screens.render("signup_otp").strip()
    assert got == want


def test_signup_screen_essentials():
    html = screens.render("signup_otp")
    assert "인증번호 입력" in html
    assert 'maxlength="6"' in html
