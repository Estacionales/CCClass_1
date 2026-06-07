# -*- coding: utf-8 -*-
"""pytest 공용 픽스처 + 패키지 경로 등록."""
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from server.contexts.eminwon.issue_svc import IssueOrchestrator  # noqa: E402
from server.integration.adapters.gw.base_adapter import GatewayAdapter  # noqa: E402
from server.shared.consent_ledger import ConsentLedger  # noqa: E402
from server.shared.eligibility import EligibilityPolicy  # noqa: E402


def agency_ok(doc_code, attempt):
    """기관이 정상 응답."""
    return {"doc": doc_code, "payload": f"{doc_code}-data"}


def agency_timeout(doc_code, attempt):
    """기관이 3초 내 미응답."""
    raise TimeoutError("agency no response within 3s")


@pytest.fixture
def agency_ok_fn():
    return agency_ok


@pytest.fixture
def agency_timeout_fn():
    return agency_timeout


@pytest.fixture
def orch():
    """(orchestrator, consent_ledger, eligibility_policy, adapter)."""
    consent = ConsentLedger()
    elig = EligibilityPolicy()
    adapter = GatewayAdapter()
    return IssueOrchestrator(consent, adapter, elig), consent, elig, adapter
