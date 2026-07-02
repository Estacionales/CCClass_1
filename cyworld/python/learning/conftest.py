# -*- coding: utf-8 -*-
"""pytest 픽스처 + 패키지 경로. 결정적: 실시간·난수 비의존."""
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from server.contexts.acorn.service import AcornService  # noqa: E402
from server.contexts.buddy.service import BuddyService  # noqa: E402
from server.contexts.chon.service import ChonService  # noqa: E402
from server.contexts.guestbook.service import GuestbookService  # noqa: E402
from server.contexts.minihomepy.service import MinihomepyService  # noqa: E402
from server.contexts.today.service import TodayService  # noqa: E402


@pytest.fixture
def chon():
    clock = {"t": 1000.0}
    svc = ChonService(clock=lambda: clock["t"])
    svc.test_clock = clock  # TTL 시간여행 테스트용 훅(선택적 사용)
    return svc


@pytest.fixture
def acorn():
    return AcornService()


@pytest.fixture
def today():
    return TodayService()


@pytest.fixture
def minihomepy(chon, acorn):
    clock = {"t": 1000.0}
    svc = MinihomepyService(chon=chon, acorn=acorn, clock=lambda: clock["t"])
    return svc, clock


@pytest.fixture
def guestbook():
    clock = {"t": 1000.0}
    svc = GuestbookService(clock=lambda: clock["t"])
    return svc, clock


@pytest.fixture
def buddy():
    clock = {"t": 1000.0}
    svc = BuddyService(clock=lambda: clock["t"])
    svc.test_clock = clock
    return svc
