# 방명록(GUESTBOOK) · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 원문: `sdd/00_sources/02_requirements/guestbook.md`

**AC-1** When 방문자가 미니홈피 방명록에 메시지를 작성하면, the system shall 메시지를
시간순으로 저장한다.

**AC-2** When 방명록 주인 또는 작성자 본인이 삭제를 요청하면, the system shall 해당
메시지를 삭제한다.

**AC-3** When 주인도 작성자도 아닌 사용자가 삭제를 요청하면, the system shall 삭제를
거부한다.

**AC-4** While 메시지가 비밀글로 작성되었을 때, when 주인·작성자가 아닌 사용자가 내용을
조회하면, the system shall 본문을 마스킹하여 응답한다.

**AC-5** When 방명록 주인이 특정 메시지에 답글을 작성하면, the system shall 해당
메시지에 답글을 1개까지만 허용한다.

**AC-6** When 이미 답글이 달린 메시지에 추가 답글을 시도하면, the system shall 거부한다.

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_guestbook.py::test_post_message_ordered` |
| AC-2·AC-3 | `tests/test_guestbook.py::test_delete_permission` |
| AC-4 | `tests/test_guestbook.py::test_secret_message_masking` |
| AC-5·AC-6 | `tests/test_guestbook.py::test_owner_reply_limit_one` |
