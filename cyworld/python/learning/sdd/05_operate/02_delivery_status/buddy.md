# 버디버디 메신저 · 배포/모니터링 현황

## 현재 라이브 베이스라인
- 환경: 로컬 단일 프로세스(DEV/PROD 구분 없는 강의 데모 저장소, `main` 브랜치 기준).
  스테이지드 DEV→PROD 롤아웃은 이 저장소의 정책·인프라에 해당 사항 없음.
- 실행: `python3 -m server.web.app` → `http://127.0.0.1:8000/`
  (런북: `sdd/05_operate/01_runbooks/buddy_local_run.md`).
- 포함 범위: 버디버디 메신저 도메인(`server/contexts/buddy/service.py`) + 화면
  (`server/contexts/buddy/screens.py`) + 라우팅(`server/web/app.py`의 `/messenger/*`).
  기존 미니홈피/일촌/방명록/도토리/투데이 도메인과 같은 프로세스에서 함께 서빙된다.

## 모니터링 베이스라인
- 결정적 proof 게이트: `python3 proof/run_proof.py` → 74/74 PASS(exit 0), 결과는
  `tmp/proof-results.json`에 기록(CI/사람이 그 파일로 회귀 여부를 즉시 확인 가능).
- 별도 APM/로그 수집 없음(로컬 데모 범위 밖) — 수동 스모크 결과는
  `sdd/04_verify/02_screen/buddy.md`에 실행 증거로 기록.

## 이번 슬라이스에서 한 일
- 2026-07-02 @backend-dev: 버디버디 메신저 신규 도메인(AC-1~AC-8) + 화면(버디 리스트·
  1:1 채팅) + 웹서버 라우팅 8종을 `sdd/01_planning`부터 구현·검증까지 진행.
- 로컬에서 실제 2인 대화 시나리오를 curl로 재현해 확인(yuna→minsu 전송 후 minsu 쪽
  폴링·페이지 렌더에 즉시 반영됨) — 상세 증거는
  `sdd/04_verify/02_screen/buddy.md`의 "수동 스모크" 섹션.

## Residual Risk
- 실 브라우저 확인은 사용자 직접 실행 권장(이 환경에 브라우저 없음, curl로 대체 검증).
- 인메모리 상태이므로 서버 재시작 시 전체 초기화(영속화 없음 — 데모 범위 밖).
- 별도 DEV/PROD 인프라·모니터링 스택이 없어 스키마 정합성·단계별 승격 절차는 해당
  없음(이 저장소는 로컬 데모 전용).
