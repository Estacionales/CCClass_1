# 버디버디 메신저(BUDDY) · 검증 (retained)

> proof: `python3 proof/run_proof.py` → 74/74 PASS (exit 0), 그 중 BUDDY 도메인 10건.
> 실행: Python 3.14.6, `tmp/proof-results.json` (2026-07-02).

| 분면 | 검증 대상 | 수용기준 | 결과 |
| --- | --- | --- | --- |
| 기능 | 요청→수락 시 양방향 관계 성립 | AC-1·AC-2 | PASS · `test_request_then_accept` |
| 검증 | PENDING 없이 수락 시 거부 | AC-2 보강 | PASS · `test_accept_without_request_rejected` |
| 멱등 | PENDING 상태에서 재요청은 중복 생성 없음 | AC-3 | PASS · `test_request_idempotent_while_pending` |
| 멱등 | 이미 버디인 상태에서 재요청은 기존 상태 반환 | AC-3 | PASS · `test_request_already_buddy_idempotent` |
| 기능 | 거절 시 요청 제거 + 이후 재요청 허용 | AC-4 | PASS · `test_reject_discards_and_allows_reask` |
| 접근제어 | 비버디 간 메시지 전송 거부 | AC-5 | PASS · `test_send_message_requires_buddy` |
| 기능 | 버디 간 메시지 시간순 저장 + 양쪽 대칭 조회 | AC-6 | PASS · `test_send_message_stored_ordered_and_symmetric` |
| 기능 | `since_id` 증분 조회(폴링 대비) | AC-6 보강 | PASS · `test_get_conversation_since_id_returns_only_new_messages` |
| 접근제어 | 상태는 버디·본인에게만 노출, 비버디는 unknown | AC-7 | PASS · `test_presence_visible_to_buddy_only` |
| 기능 | 안읽음 카운트·열람 시 읽음 처리 | AC-8 | PASS · `test_unread_count_and_mark_read` |

## Residual Risk
- 없음(계획된 AC-1~AC-8 전부 구현·검증 완료).
- CHON의 TTL(24h 만료)·정원(750) 같은 제약은 이 도메인 요구사항에 없어 의도적으로
  두지 않았다 — 향후 요구사항이 추가되면 새 슬라이스로 확장.
