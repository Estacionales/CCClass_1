# 버디버디 메신저(BUDDY) · current-state

> 03_build: Overwrite Rule(지금 상태 1벌).

## Absorbed Planning
- `01_planning/01_feature/buddy_feature_spec.md` (AC-1~AC-8 전부 구현)
- `02_plan/01_feature/buddy_todos.md` (T1~T9 전부 완료)

## Runtime Assembly
- `BuddyService.request(from_user, to_user)` → PENDING 요청 생성(이미 버디/PENDING이면 멱등)
- `BuddyService.accept(from_user, to_user)` → 양방향 버디 관계 생성 + 요청 제거
- `BuddyService.reject(from_user, to_user)` → 요청 제거, 이후 재요청 허용
- `BuddyService.is_buddy` / `buddies_of` / `pending_requests_for` → 관계·요청 조회
- `BuddyService.set_presence(user, status)` / `get_presence(user, viewer)` → 온라인/자리비움/
  오프라인, 버디·본인 외에는 "unknown"
- `BuddyService.send_message(sender, recipient, content)` → 비버디면 거부, 버디면 시간순
  저장(단일 대화 객체를 양쪽이 대칭 조회)
- `BuddyService.get_conversation(user_a, user_b, since_id=0)` → id 오름차순, 폴링용 증분 조회
- `BuddyService.unread_count(owner, buddy)` / `mark_read(owner, buddy)` → 안읽음 큐잉·읽음 처리

## Modules
| 모듈 | 책임 | AC |
| --- | --- | --- |
| `contexts/buddy/service.py` | 요청·수락·거절·멱등·전송거부·대화·상태·안읽음 | 1·2·3·4·5·6·7·8 |

## Current Behavior
사용자가 다른 사용자에게 버디 요청을 보내면 PENDING으로 남고, 상대가 수락하면 양방향
버디 관계가 되며 요청은 사라진다. 거절하면 요청만 사라지고 이후 재요청할 수 있다. 버디가
아닌 사이에서는 메시지 전송이 거부된다. 버디끼리는 메시지가 하나의 대화에 시간순으로
쌓이고 양쪽 모두 같은 순서로 조회된다. 온라인/자리비움/오프라인 상태는 버디에게만
보이고, 버디가 아닌 사용자에게는 "알수없음"으로 가려진다. 상대가 보낸 메시지는 안읽음
으로 남아있다가, 수신자가 대화를 열람하면(GET 채팅 페이지 또는 폴링 조회) 읽음 처리되어
안읽음 수가 0이 된다.

## Not Yet Implemented
- 없음(계획된 AC-1~AC-8 전부 이번 슬라이스에서 구현·검증 완료).
- CHON처럼 TTL(요청 만료)·정원 제한은 요구사항에 없어 의도적으로 두지 않았다(범위 밖).
