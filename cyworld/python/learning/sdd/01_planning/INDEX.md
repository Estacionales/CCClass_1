# 01_planning: INDEX (1단 진입점)

| 영역 | 파일 | 상태 |
| --- | --- | --- |
| feature · 일촌(CHON) | `01_feature/chon_feature_spec.md` | AC-1~AC-7 구현·검증 PASS |
| feature · 미니홈피(HOMEPY) | `01_feature/minihomepy_feature_spec.md` | AC-1~AC-6 구현·검증 PASS |
| feature · 방명록(GUESTBOOK) | `01_feature/guestbook_feature_spec.md` | AC-1~AC-6 구현·검증 PASS |
| feature · 도토리(ACORN) | `01_feature/acorn_feature_spec.md` | AC-1~AC-6 구현·검증 PASS |
| feature · 투데이(TODAY) | `01_feature/today_feature_spec.md` | AC-1~AC-3 구현·검증 PASS |
| screen · 미니홈피 | `02_screen/minihomepy_screen_spec.md` | 구현·검증 PASS(레퍼런스 이미지 스타일 반영, 웹서버 포함) |

> 폴더를 열면 이 INDEX가 먼저 보인다: 어떤 명세가 있고 어디까지 됐는지 1단으로.

## 도메인 간 의존관계
- HOMEPY의 일촌공개 접근제어(AC-4) → CHON의 일촌 관계 조회에 의존.
- HOMEPY의 스킨/BGM 적용(AC-6) → ACORN의 인벤토리 조회에 의존.
- GUESTBOOK은 사용자 존재 여부 외 다른 도메인에 직접 의존하지 않음.

## 다음 단계
- `sdd/02_plan/01_feature/*_todos.md`, `02_plan/02_screen/minihomepy_screen_todos.md` :
  실행 계획.
- 5개 도메인 + 미니홈피 화면·웹서버 전부 `python3 proof/run_proof.py` → 51/51 PASS
  (exit 0, Python 3.14.6, `tmp/proof-results.json`)로 검증됨. 상세는
  `sdd/04_verify/01_feature/*.md`, `sdd/04_verify/02_screen/minihomepy.md`.
- CHON은 AC-1~AC-7, ACORN은 AC-1~AC-6 전부 완료 — 계획된 MVP AC가 모두 구현·검증됨.
- 미니홈피 화면은 `sdd/00_sources/image.png` 레퍼런스 스타일(바인더 프레임·그리드
  텍스처·사이드바·탭)로 재구성됨. Miniroom·프로필 사진은 실 자산 없어 자리표시자로 대체
  (`sdd/04_verify/02_screen/minihomepy.md`의 Residual Risk 참고).
- `python3 -m server.web.app`으로 실행 가능(`http://127.0.0.1:8000/`).
- 남은 것: `sdd/05_operate` 배포·모니터링 기록(아직 롤아웃 없음), 신규 기능 확장 시 새 슬라이스.
