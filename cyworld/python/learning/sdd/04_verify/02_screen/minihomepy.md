# 미니홈피 화면 · 검증 (retained)

> proof: `python3 proof/run_proof.py` → 51/51 PASS (exit 0), 그 중 화면·웹서버·프로필
> 관련 신규/변경 테스트 다수. 실행: Python 3.14.6, `tmp/proof-results.json` (2026-07-02).
> 이 환경은 브라우저·Playwright가 없어 렌더 유닛테스트 + 실제 WSGI 서버 기동 후 curl
> 스모크로 대체 검증했다(`sdd/01_planning/02_screen/minihomepy_screen_spec.md`에 경계 명시).

## 자동 테스트 (레퍼런스 스타일 재구성분)

| 분면 | 검증 대상 | 결과 |
| --- | --- | --- |
| 렌더 | 통계 바(TODAY/TOTAL, 천단위 콤마) | PASS · `test_render_stats_bar` |
| 렌더 | 프로필 사이드바(무드·캡션·파도타기·빈 상태) | PASS · `test_render_profile_sidebar` |
| 렌더 | 다이어리 공개범위 라벨 | PASS · `test_render_diary_visibility` |
| 렌더 | 방명록 마스킹·답글·hidden viewer | PASS · `test_render_guestbook` |
| 렌더 | What Friends say(마스킹 항목 제외) | PASS · `test_render_friends_say_hides_masked_entries` |
| 렌더 | 탭 네비게이션(홈 활성/사진첩 비활성) | PASS · `test_render_nav_tabs_marks_active` |
| 보안 | 프로필 포함 전체 입력 HTML 이스케이프(XSS) | PASS · `test_render_escapes_user_content` |
| 렌더 | 페이지 조립(프레임/타이틀/섹션 전부 포함) | PASS · `test_render_page_assembles_sections` |
| 기능(백엔드) | 프로필 설정/조회 | PASS · `test_minihomepy.py::test_set_and_get_profile` |
| 기능(백엔드) | 다이어리 개수(공개범위 무관 전체) | PASS · `test_minihomepy.py::test_diary_count_counts_all_regardless_of_visibility` |
| 기능(백엔드) | 오늘 방문자수 일 단위 리셋, 누적 TOTAL은 유지 | PASS · `test_minihomepy.py::test_visits_today_resets_on_new_day` |
| 기능(백엔드) | 방명록 개수 조회 | PASS · `test_guestbook.py::test_count_returns_owner_message_total` |

## 수동 스모크 (실행 증거)
1. `python3 -m server.web.app` 재기동(레퍼런스 스타일 적용 버전).
2. `GET /minihomepy/yuna?viewer=minsu` → 렌더된 HTML에서 다음을 직접 확인:
   - `class="frame"` (바인더 프레임 컨테이너)
   - `TODAY 1 | TOTAL 1` (오늘/누적 방문자 통계, minsu의 첫 방문)
   - `유나의 추억 상자..♡` (닉네임 기반 타이틀)
   - `TODAY IS... 감성` (무드뱃지, 시드 프로필 반영)
   - 다이어리 카드: 전체공개·일촌공개 두 항목만 노출(minsu는 일촌, 비공개는 숨김 —
     기존 접근제어 로직이 프로필 확장 후에도 그대로 동작함을 재확인)
   - 방명록 카드: minsu 메시지 + 주인 답글, stranger의 비밀글은 `***`로 마스킹
   - 우측 탭 4개(홈 active, 사진첩 disabled, 다이어리/방명록 앵커) 렌더 확인
3. 검증 후 서버 프로세스 종료.

## Residual Risk
- **일러스트 자산 없음**: Miniroom 픽셀아트·프로필 사진은 이 환경에 이미지 생성/자산
  빌더가 없어 이모지 자리표시자로 대체했다. 레이아웃·색감·문구는 레퍼런스를 따랐지만
  그림 자체는 재현하지 않았다 — 실 자산이 생기면 `photo-placeholder`·`miniroom-scene`
  블록만 교체하면 되도록 CSS 클래스를 분리해뒀다.
- **브라우저 픽셀 비교 없음**: 렌더 결과를 curl로 가져와 문자열 단위로 확인했을 뿐,
  실제 브라우저 렌더링(폰트 대체, flexbox 실제 계산 등)과 시각적으로 100% 일치하는지는
  확인하지 못했다. 사용자가 `python3 -m server.web.app` 실행 후 직접 브라우저로 열어
  확인하는 것을 권장한다.
- 실 로그인/세션 없음(이전 슬라이스와 동일한 알려진 제약).
