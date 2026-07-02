# 01_planning: INDEX (1단 진입점)

| 영역 | 파일 | 상태 |
| --- | --- | --- |
| feature · 일촌(CHON) | `01_feature/chon_feature_spec.md` | AC-1~AC-7 구현·검증 PASS |
| feature · 미니홈피(HOMEPY) | `01_feature/minihomepy_feature_spec.md` | AC-1~AC-6 구현·검증 PASS |
| feature · 방명록(GUESTBOOK) | `01_feature/guestbook_feature_spec.md` | AC-1~AC-6 구현·검증 PASS |
| feature · 도토리(ACORN) | `01_feature/acorn_feature_spec.md` | AC-1~AC-6 구현·검증 PASS |
| feature · 투데이(TODAY) | `01_feature/today_feature_spec.md` | AC-1~AC-3 구현·검증 PASS |
| feature · 버디버디 메신저(BUDDY) | `01_feature/buddy_feature_spec.md` | AC-1~AC-8 구현·검증 PASS |
| screen · 미니홈피 | `02_screen/minihomepy_screen_spec.md` | 구현·검증 PASS(레퍼런스 이미지 스타일 반영, 웹서버 포함) |
| screen · 버디버디 메신저 | `02_screen/buddy_screen_spec.md` | 구현·검증 PASS(원 인터페이스, 로컬 2인 대화 웹 UI 포함) |

> 폴더를 열면 이 INDEX가 먼저 보인다: 어떤 명세가 있고 어디까지 됐는지 1단으로.

## 도메인 간 의존관계
- HOMEPY의 일촌공개 접근제어(AC-4) → CHON의 일촌 관계 조회에 의존.
- HOMEPY의 스킨/BGM 적용(AC-6) → ACORN의 인벤토리 조회에 의존.
- GUESTBOOK은 사용자 존재 여부 외 다른 도메인에 직접 의존하지 않음.
- BUDDY는 사용자 존재 여부 외 다른 도메인(CHON 등)에 직접 의존하지 않는 독립 도메인.

## 다음 단계
- `sdd/02_plan/01_feature/*_todos.md`, `02_plan/02_screen/minihomepy_screen_todos.md`,
  `02_plan/02_screen/buddy_screen_todos.md` : 실행 계획.
- 6개 도메인(CHON·HOMEPY·GUESTBOOK·ACORN·TODAY·BUDDY) + 미니홈피/버디버디 화면·웹서버
  전부 `python3 proof/run_proof.py` 로 검증됨(회귀 포함 전체 PASS, exit 0, Python 3.14.6,
  `tmp/proof-results.json`). 상세는 `sdd/04_verify/01_feature/*.md`,
  `sdd/04_verify/02_screen/*.md`.
- CHON은 AC-1~AC-7, ACORN은 AC-1~AC-6, BUDDY는 AC-1~AC-8 전부 완료 — 계획된 MVP AC가
  모두 구현·검증됨.
- 미니홈피 화면은 `sdd/00_sources/image.png` 레퍼런스 스타일(바인더 프레임·그리드
  텍스처·사이드바·탭)로 재구성됨. Miniroom·프로필 사진은 실 자산 없어 자리표시자로 대체
  (`sdd/04_verify/02_screen/minihomepy.md`의 Residual Risk 참고).
- 버디버디 메신저 화면은 참조 이미지가 없어 요구사항에서 직접 도출한 원 인터페이스로
  설계됨(버디 리스트 + 1:1 채팅, 2초 폴링). 로컬에서 두 브라우저 창으로 2인 실사용 가능
  (`sdd/04_verify/02_screen/buddy.md`, `sdd/05_operate` 참고).
- `python3 -m server.web.app`으로 실행 가능(`http://127.0.0.1:8000/`).
- 남은 것: 신규 기능 확장 시 새 슬라이스. 현재 `sdd/05_operate`에 로컬 실행 기준
  배포·모니터링 기록 완료(별도 DEV/PROD 인프라 없는 로컬 데모 환경).
