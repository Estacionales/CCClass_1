# 싸이월드(미니홈피) 데모 — MVP 구현 상태

> 강의 데모용 **가상** 싸이월드(미니홈피) 서비스입니다. 실재 개인정보 없음.
> `auth/python/learning`과 동일한 SDD 5단계 방법론(01_planning → 05_operate)을
> 그대로 적용해, 6개 MVP 도메인(일촌·미니홈피·방명록·도토리·투데이·버디버디)을
> 계획·구현했습니다.

## MVP 도메인
| 코드 | 도메인 | 요약 | 상태 |
| --- | --- | --- | --- |
| CHON | 일촌(一寸) | 신청·수락·TTL만료·정원750·파일촌·일촌평(AC-1~AC-7) | 구현·검증 PASS |
| HOMEPY | 미니홈피 | 자동생성·다이어리 공개범위·방문자수·아이템 적용(AC-1~AC-6) | 구현·검증 PASS |
| GUESTBOOK | 방명록 | 작성·삭제권한·비밀글·답글제한(AC-1~AC-6) | 구현·검증 PASS |
| ACORN | 도토리 | 충전·구매·선물·거래내역·멱등(AC-1~AC-6) | 구현·검증 PASS |
| TODAY | 투데이 | 하루 1회 등록(AC-1~AC-3) | 구현·검증 PASS |
| BUDDY | 버디버디 메신저 | 버디 요청·수락·거절·전송거부·1:1 채팅·상태·안읽음(AC-1~AC-8) | 구현·검증 PASS |

## 버디버디 메신저 웹 화면(2인 로컬 대화)
버디 리스트(`/messenger/<user>`)에서 버디 요청·수락/거절·온라인 상태를 관리하고,
1:1 채팅(`/messenger/<user>/<buddy>`)에서 실제로 메시지를 주고받을 수 있다(2초 폴링,
WebSocket 없이 표준 라이브러리만으로 구현). 서버를 하나 띄운 채 브라우저 창(또는
시크릿 창) 두 개를 각각 `/messenger/yuna/minsu`, `/messenger/minsu/yuna`로 열면
두 사람이 대화하는 것처럼 실사용해볼 수 있다. 자세한 사용법은
`sdd/05_operate/01_runbooks/buddy_local_run.md` 참고.

## 미니홈피 웹 화면
표준 라이브러리 `wsgiref`만으로 만든 실행 가능한 데모 웹서버(외부 프레임워크 의존 없음).
`sdd/00_sources/image.png` 레퍼런스 스타일(하늘색 바인더 프레임·회색 그리드 텍스처
배경·좌측 프로필 사이드바·상단 방문자 통계·우측 탭 네비게이션)을 CSS로 재현했다.
```bash
python3 -m server.web.app        # → http://127.0.0.1:8000/
```
시드 데이터로 `yuna`(주인)·`minsu`(일촌) 두 사용자가 준비되어 있다.
`/minihomepy/yuna?viewer=minsu`처럼 `viewer` 쿼리로 접근제어(전체공개/일촌공개/비공개)를
바로 확인할 수 있다. 방명록 작성 폼은 실제 POST로 동작한다.

> Miniroom 픽셀아트·프로필 사진은 실 이미지 자산이 없어 이모지 자리표시자로 대체했다.
> 브라우저가 없는 환경이라 curl/유닛테스트로만 검증했으니, 직접 브라우저로 열어
> 확인해보는 것을 권장한다.

## 산출물
- `sdd/00_sources/02_requirements/*.md` : 도메인별 요구사항 원문
- `sdd/01_planning/01_feature/*_feature_spec.md`, `01_planning/02_screen/*.md` : EARS AC·화면 명세
- `sdd/02_plan/01_feature/*_todos.md`, `02_plan/02_screen/*.md` : 도메인·화면별 todos·실행 계획
- `sdd/02_plan/10_test/regression_verification.md` : 도메인 간 공유 표면(회귀 범위) + 결과
- `sdd/03_build/01_feature/*.md`, `03_build/02_screen/*.md` : 현재 구현 상태 요약
- `sdd/04_verify/01_feature/*.md`, `04_verify/02_screen/*.md` : proof 실행 증거 기반 검증 기록
- `sdd/05_operate/01_runbooks/*.md`, `05_operate/02_delivery_status/*.md` : 로컬 실행
  런북·배포 현황
- `server/contexts/{chon,minihomepy,guestbook,acorn,today,buddy}/service.py` : 도메인 구현
- `server/contexts/minihomepy/screens.py`, `server/contexts/buddy/screens.py` : 화면 렌더(순수 함수)
- `server/web/app.py` : WSGI 웹서버(라우팅 + 시드 데이터, 6개 도메인 전부 서빙)
- `tests/test_{chon,minihomepy,guestbook,acorn,today,buddy}.py`,
  `tests/test_minihomepy_screen.py`, `tests/test_buddy_screen.py`, `tests/test_web_app.py` :
  proof 게이트 테스트

## 도메인 간 의존관계
- 미니홈피 다이어리의 '일촌공개' 접근제어는 CHON의 `is_chon()` 조회에 의존한다.
- 미니홈피 스킨/BGM 적용은 ACORN의 `inventory` 조회에 의존한다.
- `MinihomepyService`는 `ChonService`·`AcornService` 인스턴스를 생성자 주입으로 참조한다
  (단일 프로세스 데모, 별도 API 계약 없음).
- 방명록·투데이·버디버디는 사용자 존재 여부 외 다른 도메인에 직접 의존하지 않는다
  (버디버디는 CHON의 일촌 개념과 별개의 독립적인 버디 관계망이다).

## 검증
```bash
python3 -m pip install -r requirements.txt
python3 proof/run_proof.py        # → 74/74 PASS (exit 0)
```

## 남은 범위 (다음 세션)
- 계획된 6개 도메인 + 미니홈피/버디버디 화면·웹서버는 전부 구현·검증 완료.
- 실 로그인/세션 없음(데모는 `viewer` 쿼리 파라미터 또는 URL 경로 세그먼트로 신원 대체).
- `sdd/05_operate` : 로컬 실행 기준 배포·모니터링 기록 완료(별도 DEV/PROD 인프라 없는
  로컬 데모 환경, `05_operate/01_runbooks/buddy_local_run.md` 참고).
