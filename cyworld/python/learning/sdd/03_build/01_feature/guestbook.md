# 방명록(GUESTBOOK) · current-state

> 03_build: Overwrite Rule(지금 상태 1벌).

## Absorbed Planning
- `01_planning/01_feature/guestbook_feature_spec.md` (AC-1~AC-6 전부 구현)
- `02_plan/01_feature/guestbook_todos.md` (T1~T5 전부 완료)

## Runtime Assembly
- `GuestbookService.post(owner, author, content, secret=False)` → 시간순 메시지 저장
- `GuestbookService.list_messages(owner)` → ts 오름차순 id 목록
- `GuestbookService.delete(msg_id, requester)` → 주인·작성자만 허용
- `GuestbookService.read(msg_id, viewer)` → 비밀글은 주인·작성자 외 마스킹("***")
- `GuestbookService.reply(msg_id, owner, content)` → 메시지당 답글 1개 제한

## Modules
| 모듈 | 책임 | AC |
| --- | --- | --- |
| `contexts/guestbook/service.py` | 작성·조회·삭제·비밀글·답글제한 | 1·2·3·4·5·6 |

## Current Behavior
방문자가 메시지를 남기면 시간순으로 저장된다. 주인 또는 작성자 본인만 삭제할 수 있고,
그 외 요청은 거부된다. 비밀글은 주인·작성자가 아닌 조회자에게 본문 대신 마스킹 문자열을
반환한다. 주인은 메시지당 답글을 1개까지만 남길 수 있다.

## Not Yet Implemented
- 없음(계획된 AC-1~AC-6 전부 이번 슬라이스에서 구현·검증 완료).
