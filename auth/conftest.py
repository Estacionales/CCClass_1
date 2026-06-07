# -*- coding: utf-8 -*-
"""pytest 픽스처 + 패키지 경로. 결정적: 고정 OTP + 제어 가능한 시계."""
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from server.contexts.auth.otp import OTPService  # noqa: E402
from server.contexts.auth.signup import SignupService  # noqa: E402


@pytest.fixture
def otp():
    clock = {"t": 1000.0}
    svc = OTPService(ttl_s=300, max_attempts=5,
                     clock=lambda: clock["t"], otp_gen=lambda: "123456")
    return svc, clock


@pytest.fixture
def signup(otp):
    svc, clock = otp
    return SignupService(svc), svc, clock
