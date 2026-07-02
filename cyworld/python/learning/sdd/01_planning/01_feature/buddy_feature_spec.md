# 버디버디 메신저(BUDDY) · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 원문: `sdd/00_sources/02_requirements/buddy-messenger.md`

**AC-1** When 사용자가 다른 사용자에게 버디 요청을 보내면, the system shall PENDING
상태의 버디 요청을 생성한다.

**AC-2** While 요청이 PENDING일 때, when 상대가 수락하면, the system shall 양방향 버디
관계를 생성하고 해당 요청을 제거한다.

**AC-3** When 이미 버디 관계이거나 PENDING 요청이 존재하는 대상에게 재요청하면, the
system shall 중복 생성 없이 기존 상태를 반환한다(멱등).

**AC-4** While 요청이 PENDING일 때, when 상대가 거절하면, the system shall 요청을
제거하고 이후 재요청을 허용한다.

**AC-5** While 두 사용자가 버디 관계가 아닐 때, when 어느 한쪽이 메시지 전송을 시도하면,
the system shall 전송을 거부한다.

**AC-6** When 버디 사이에서 메시지를 주고받으면, the system shall 하나의 대화에 시간순
으로 저장하고 양쪽 사용자에게 동일한 순서로 조회되게 한다.

**AC-7** When 사용자가 온라인/자리비움/오프라인 상태를 설정하면, the system shall 그
상태를 버디에게만 노출하고 버디가 아닌 사용자에게는 노출하지 않는다.

**AC-8** While 상대가 보낸 메시지가 안읽음 상태일 때, when 수신자가 해당 대화를
열람하면, the system shall 그 버디가 보낸 메시지를 모두 읽음 처리하고 안읽음 수를
0으로 만든다.

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1·AC-2 | `tests/test_buddy.py::test_request_then_accept` |
| AC-3 | `tests/test_buddy.py::test_request_idempotent_while_pending`, `test_request_already_buddy_idempotent` |
| AC-4 | `tests/test_buddy.py::test_reject_discards_and_allows_reask` |
| AC-5 | `tests/test_buddy.py::test_send_message_requires_buddy` |
| AC-6 | `tests/test_buddy.py::test_send_message_stored_ordered_and_symmetric` |
| AC-7 | `tests/test_buddy.py::test_presence_visible_to_buddy_only` |
| AC-8 | `tests/test_buddy.py::test_unread_count_and_mark_read` |
