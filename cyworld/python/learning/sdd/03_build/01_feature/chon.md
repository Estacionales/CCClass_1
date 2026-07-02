# 일촌(CHON) · current-state

> 03_build: Overwrite Rule(지금 상태 1벌).

## Absorbed Planning
- `01_planning/01_feature/chon_feature_spec.md` (AC-1~AC-7 전부 구현)
- `02_plan/01_feature/chon_todos.md` (T1~T5 전부 완료)

## Runtime Assembly
- `ChonService.request(from_user, to_user)` → PENDING 신청 생성(이미 일촌/유효한 PENDING이면
  그 상태 반환). 기존 PENDING이 TTL 초과 상태면 만료 처리 후 새 PENDING 생성.
- `ChonService.accept(from_user, to_user)` → 만료 검증 → 정원(750) 검증 → 양방향 `_chon`
  관계 성립
- `ChonService.unchon(user_a, user_b)` → 양쪽 목록에서 동시에 관계 제거(파일촌)
- `ChonService.write_chonpyeong(from_user, to_user, text)` → 일촌 관계 검증 후 저장
- `ChonService.is_chon(a, b)` → 관계 조회

## Modules
| 모듈 | 책임 | AC |
| --- | --- | --- |
| `contexts/chon/service.py` | 신청·수락·만료·정원·파일촌·일촌평·관계조회 | 1·2·3·4·5·6·7 |

## Current Behavior
신청 → PENDING(발급 시각 기록) → 24시간 이내 수락 시 양방향 일촌 관계 생성. TTL 초과 후
수락 시도는 거부(reason=expired)되며, 이후 재신청은 새 PENDING으로 허용된다. 어느 한쪽이
이미 750명 정원에 도달한 상태에서 수락하면 거부된다(reason=capacity_exceeded). 일촌
해제(파일촌)는 양쪽 목록에서 동시에 제거된다. 일촌평은 일촌 관계가 성립한 사이에서만
작성할 수 있다.

## Not Yet Implemented
- 없음(계획된 AC-1~AC-7 전부 이번 슬라이스에서 구현·검증 완료).
