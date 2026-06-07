# -*- coding: utf-8 -*-
"""회귀 — 기존 로그인 흐름(shared surface)이 회원가입 추가로 깨지지 않는다."""
from server.contexts.auth.login import LoginService


def test_regression_login_existing_account(signup):
    sv, otp, _ = signup
    otp.issue("a@x.com")
    sv.signup("a@x.com", "123456")
    login = LoginService(sv.accounts)
    assert login.login("a@x.com")["status"] == "ok"
    assert login.login("nobody@x.com")["status"] == "denied"
