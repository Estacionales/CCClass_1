# 회귀 검증 범위 (retained)

> proof: `python3 proof/run_proof.py` → 74/74 PASS (exit 0), Python 3.14.6,
> `tmp/proof-results.json` (2026-07-02).

| 표면 | 분류 | 검증 | 결과 |
| --- | --- | --- | --- |
| 일촌 신청·수락·만료·정원·파일촌·일촌평(AC-1~AC-7) | direct | `test_chon.py` (10건) | PASS |
| 미니홈피 다이어리·프로필·방문자수·상태메시지·카운트 | direct | `test_minihomepy.py` (9건) | PASS |
| 방명록 작성·삭제·답글·개수 | direct | `test_guestbook.py` (5건) | PASS |
| 도토리 충전·구매·선물·거래내역(AC-1~AC-6) | direct | `test_acorn.py` (9건) | PASS |
| 투데이 하루 1회 등록(AC-1~AC-3) | direct | `test_today.py` (3건) | PASS |
| 버디버디 요청·수락·거절·멱등·전송거부·대화·상태·안읽음(AC-1~AC-8) | direct | `test_buddy.py` (10건) | PASS |
| 미니홈피 화면 렌더(레퍼런스 스타일, 순수 함수) | direct | `test_minihomepy_screen.py` (8건) | PASS |
| 버디버디 화면 렌더(원 인터페이스, 순수 함수) | direct | `test_buddy_screen.py` (5건) | PASS |
| 웹서버 라우팅(미니홈피/방명록 + 메신저) | direct+shared | `test_web_app.py` (15건) | PASS |
| 미니홈피 → 일촌 관계 조회 | shared | `test_minihomepy.py::test_diary_visibility_chon_only` | PASS |
| 미니홈피 → 도토리 인벤토리 조회 | shared | `test_minihomepy.py::test_skin_bgm_requires_inventory` | PASS |
| 웹서버 → 미니홈피/방명록/일촌/도토리/버디버디 서비스 전체 연동 | shared | `test_web_app.py`(시드 데이터로 5개 서비스 실 인스턴스 조립, `build_services`/
  `seed_demo_data`/`make_app` 5-튜플 시그니처 변경 후 기존 케이스 전량 재실행) | PASS |

선정 근거: 미니홈피는 접근제어(일촌공개)와 스킨/BGM 적용(인벤토리)에서 CHON·ACORN을
직접 조회하므로, 두 도메인의 변경이 미니홈피 회귀 범위에 포함된다. GUESTBOOK·BUDDY는
사용자 존재 여부 외 교차 의존이 없어 direct 범위로만 검증한다(버디버디는 CHON의 일촌
개념과 별개의 독립 관계망이다 — 의도적으로 재사용하지 않음, `sdd/01_planning/INDEX.md`
참고). shared 표면 테스트는 CHON·ACORN 스텁이 아닌 실 서비스 인스턴스를 주입해
실행했다. 버디버디는 웹서버 조립 함수(`build_services`/`seed_demo_data`/`make_app`)의
시그니처를 4-튜플→5-튜플로 바꿔야 했으므로, 이 변경이 기존 미니홈피/방명록 라우팅에
회귀를 일으키지 않는지 `test_web_app.py`의 기존 7건을 전부 함께 재실행해 확인했다
(회귀 없음). 화면 렌더(프로필/카운트 확장) 32건 + 버디버디 신규 백엔드·화면·라우팅
23건 = 74건 전부 PASS했다.

## 남은 범위 밖 AC
- 없음. 계획된 6개 도메인(CHON·HOMEPY·GUESTBOOK·ACORN·TODAY·BUDDY)의 전체 AC와
  미니홈피·버디버디 화면·웹서버가 구현·검증 완료됐다. 향후 확장은 새 요구사항으로
  시작하는 다음 슬라이스로 취급한다.
