# 미니홈피(HOMEPY) · current-state

> 03_build: Overwrite Rule(지금 상태 1벌).

## Absorbed Planning
- `01_planning/01_feature/minihomepy_feature_spec.md` (AC-1~AC-6 전부 구현)
- `02_plan/01_feature/minihomepy_todos.md` (T1~T5 전부 완료)

## Runtime Assembly
- `MinihomepyService.create_for_user(user)` → 미니홈피 존재 마커 생성(멱등: 이미 있으면 exists)
- `MinihomepyService.write_diary/read_diary` → 공개범위(public/chon/private) 접근제어.
  chon 공개범위는 주입된 `ChonService.is_chon(author, viewer)`로 판정
- `MinihomepyService.visit(owner, visitor)` → 본인 방문 제외, 24시간 내 재방문 dedup
- `MinihomepyService.apply_item(user, item_id)` → 주입된 `AcornService.inventory`에 보유한
  아이템만 적용 허용

## Modules
| 모듈 | 책임 | AC |
| --- | --- | --- |
| `contexts/minihomepy/service.py` | 자동생성·다이어리 접근제어·방문자수·아이템 적용 | 1·2·3·4·5·6 |

## Cross-context Dependency
- `chon`(ChonService)와 `acorn`(AcornService)을 생성자 주입으로 참조한다(공유 저장소 직접
  참조, 별도 API 계약 없음 — 단일 프로세스 데모 범위).

## Current Behavior
회원가입 훅(`create_for_user`) 호출 시 미니홈피가 생성된다. 다이어리는 작성자 본인은 항상
조회 가능하고, private은 본인만, chon은 일촌 관계인 사용자만 조회 가능하다. 방문은 본인
방문을 세지 않고 동일 방문자의 24시간 내 재방문을 중복 카운트하지 않는다. 스킨/BGM은
acorn 인벤토리에 없는 아이템은 적용을 거부한다.

## Not Yet Implemented
- 스킨/BGM 실제 렌더링(화면 적용 결과 표시)은 범위 밖 — 적용 상태 저장까지만 구현.
- 회원가입 서비스 자체는 이 프로젝트에 없음(`create_for_user`는 가입 완료 시 호출될 훅).
