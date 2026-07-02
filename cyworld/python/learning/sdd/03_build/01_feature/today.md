# 투데이(TODAY) · current-state

> 03_build: Overwrite Rule(지금 상태 1벌).

## Absorbed Planning
- `01_planning/01_feature/today_feature_spec.md` (AC-1~AC-3 구현)
- `02_plan/01_feature/today_todos.md` (T1·T2 완료)

## Runtime Assembly
- `TodayService.check_in(user, day)` → 해당 `day`에 최초 등록이면 recorded, 이미 있으면
  already(멱등). `day`는 호출자가 주입하는 "YYYY-MM-DD" 문자열(실시간 비의존).

## Modules
| 모듈 | 책임 | AC |
| --- | --- | --- |
| `contexts/today/service.py` | 하루 1회 등록 + 날짜 기준 멱등 | 1·2·3 |

## Current Behavior
사용자별로 등록된 날짜 집합을 관리한다. 같은 날짜 재등록은 already로 응답하고 상태를
바꾸지 않는다. 날짜가 바뀌면 다시 recorded로 등록할 수 있다.
