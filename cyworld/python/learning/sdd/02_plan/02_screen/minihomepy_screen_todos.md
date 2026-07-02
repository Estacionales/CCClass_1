# 미니홈피 화면 · todos + 실행 계획

## Scope
`sdd/01_planning/02_screen/minihomepy_screen_spec.md` 기준 화면(미니홈피 프로필·통계·
방명록·다이어리)과 이를 서빙하는 실행 가능한 WSGI 웹서버 구현. 2026-07-02 두 번째
요청으로 `sdd/00_sources/image.png` 레퍼런스 스타일(바인더 프레임·그리드 텍스처·사이드바·
탭 네비게이션)에 맞춰 재구성.

## Acceptance Criteria
- 다이어리는 공개범위(전체/일촌/비공개)에 따라 viewer별로 다르게 렌더된다.
- 방명록은 비밀글 마스킹·주인 답글이 렌더에 반영된다.
- 사용자 입력(프로필·다이어리·방명록)은 HTML 이스케이프되어 XSS가 발생하지 않는다.
- 레퍼런스 이미지의 프레임/텍스처/사이드바/통계바/탭 레이아웃을 CSS로 재현한다.
- 서버가 실제로 기동해 GET/POST 요청에 정상 응답한다(수동 스모크).
- proof 게이트 exit 0 = 완료.

## Execution Checklist (비중첩)
- [x] T1 @backend-dev  1차 렌더 함수 + WSGI 서버(2026-07-02 첫 요청, 완료)
- [x] T2 @backend-dev  프로필(닉네임/무드/상태메시지) + diary_count/guestbook.count +
      오늘/전체 방문자수 분리(`visits_today`) 추가
- [x] T3 @frontend-dev 레퍼런스 스타일 재구성: 바인더 프레임(binder-hole)·그리드 텍스처
      배경·좌측 사이드바(무드뱃지·사진 자리표시자·캡션·파도타기 버튼)·통계바·뮤직 플레이어
      자리표시자·What Friends say·Miniroom 자리표시자·우측 세로 탭 (`screens.py` 전면 재작성)
- [x] T4 @frontend-dev `server/web/app.py` 뷰모델 배선(프로필·카운트·오늘/전체 방문자수)
- [x] T5 @test-dev     렌더 유닛테스트 갱신(`tests/test_minihomepy_screen.py`, 새 함수 시그니처)
- [x] T6 @test-dev     신규 백엔드 메서드 테스트(`test_minihomepy.py`·`test_guestbook.py`)
- [x] T7 @frontend-dev 수동 스모크: 서버 재기동 + curl로 프레임·통계바·사이드바 렌더 확인

## Regression Scope
- direct: 화면·웹서버(`server/web`, `server/contexts/minihomepy/screens.py`)
- shared: `MinihomepyService`(profile/diary_count/visits_today 추가)·
  `GuestbookService`(count 추가) — 두 서비스의 기존 pytest가 회귀 게이트 역할
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Current Notes
- 2026-07-02 @frontend-dev 요청으로 최초 구현(단순 카드 레이아웃).
- 2026-07-02 같은 날 재요청: `sdd/00_sources/image.png` 레퍼런스에 맞춰 전면 재스타일링.
  실제 일러스트(Miniroom 픽셀아트, 프로필 사진)는 자산이 없어 이모지 자리표시자로 대체 —
  `sdd/01_planning/02_screen/minihomepy_screen_spec.md`의 "알려진 자산 경계"에 기록.
- 이전 슬라이스에서 발견한 손상 인코딩 POST 500 버그 수정은 유지됨(회귀 없음, 재테스트 PASS).

## Validation
- `python3 proof/run_proof.py` → 51/51 PASS (exit 0), 신규/변경 테스트 포함
  (`test_minihomepy_screen.py` 8건, `test_minihomepy.py`·`test_guestbook.py` 백엔드
  추가분 4건).
- 수동 스모크: `python3 -m server.web.app` 기동 → curl `/minihomepy/yuna?viewer=minsu` →
  `class="frame"`, `TODAY n | TOTAL n`, `유나의 추억 상자..♡`, `TODAY IS... 감성` 등
  레퍼런스 대응 요소가 렌더된 HTML에 존재함을 확인 후 서버 종료.
