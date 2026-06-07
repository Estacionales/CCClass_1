# -*- coding: utf-8 -*-
"""로그인 — 기존 흐름(회귀 검증 대상 shared surface)."""


class LoginService:
    def __init__(self, accounts):
        self.accounts = accounts

    def login(self, email):
        return {"status": "ok"} if email in self.accounts else {"status": "denied"}
