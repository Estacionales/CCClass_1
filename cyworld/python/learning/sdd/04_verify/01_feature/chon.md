# 일촌(CHON) · 검증 (retained)

> proof: `python3 proof/run_proof.py` → 28/28 PASS (exit 0), 그 중 CHON 10건.
> 실행: Python 3.14.6, `tmp/proof-results.json` (2026-07-02).

| 분면 | 검증 대상 | 수용기준 | 결과 |
| --- | --- | --- | --- |
| 기능 | 신청→수락 성립(양방향) | AC-1·AC-2 | PASS · `test_request_then_accept` |
| 검증 | 대기 요청 없이 수락 시도 | - | PASS · `test_accept_without_request_rejected` |
| 멱등 | PENDING 상태 재신청 시 중복 생성 없음 | AC-3 | PASS · `test_request_idempotent_while_pending` |
| 멱등 | 이미 일촌인 대상 재신청 시 accepted 유지 | AC-3 | PASS · `test_request_already_chon` |
| 만료 | TTL(24h) 초과 후 수락 거부 + 재신청 허용 | AC-4 | PASS · `test_request_expiry_allows_reaccept` |
| 만료 | TTL 이내 재신청은 멱등 유지 | AC-4 | PASS · `test_request_not_expired_within_ttl` |
| 정원 | 750명 도달 시 신규 수락 거부 | AC-5 | PASS · `test_chon_capacity_750_rejects_accept` |
| 파일촌 | 해제 시 양쪽에서 동시 제거 | AC-6 | PASS · `test_unchon_removes_both_sides` |
| 검증 | 일촌 아닌 관계 해제 시도 거부 | AC-6 | PASS · `test_unchon_when_not_chon_rejected` |
| 일촌평 | 일촌 관계 검증(비일촌 거부 → 일촌 성립 후 작성 허용) | AC-7 | PASS · `test_chonpyeong_requires_chon` |

## Residual Risk
- 없음(계획된 AC-1~AC-7 전부 구현·검증 완료).
- 정원(750) 테스트는 white-box로 내부 `_chon` 딕셔너리를 직접 세팅해 750회 `accept()`
  루프를 피했다 — 동작은 동일하지만 실 `request`/`accept` 경로를 750회 왕복하지는 않는다.
