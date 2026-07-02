# 미니홈피 화면 · 명세

> 소스: `sdd/00_sources/image.png` (레퍼런스 목업 — 하늘색 바인더 프레임 + 회색 그리드
> 텍스처 배경 + 좌측 프로필 사이드바 + 상단 방문자 통계 + 우측 세로 탭 네비게이션).
> 이 환경엔 Asset Spec Builder·디자인 가이드 빌더가 없어(`sdd/99_toolchain` 미보유),
> 레퍼런스를 직접 관찰해 CSS로 수동 해석했다 — 그 경계(특히 일러스트 자산)는
> `sdd/04_verify/02_screen/minihomepy.md`에 기록한다.
> 실 강의의 Playwright exactness 대신, 이 환경에서는 실행 가능한 WSGI 서버 + 결정적
> HTML 렌더 함수 유닛테스트로 검증한다(브라우저 비가용).

## 레이아웃 (`GET /minihomepy/<owner>?viewer=<viewer>`)

| 영역 | 레퍼런스 요소 | 이 구현의 데이터 소스 |
| --- | --- | --- |
| 프레임 | 하늘색(#4fc3e8) 10px 라운드 보더 + 상단 바인더 구멍 2개 | CSS만(`.frame`, `::before/::after`) |
| 배경 텍스처 | 연회색 그리드 패턴 | CSS `linear-gradient` 반복 패턴(`body`) |
| 상단 헤더 | `TODAY n | TOTAL n,nnn` + 타이틀 + 브랜드 | `MinihomepyService.visits_today/visitor_counts` |
| 좌측 사이드바 | 무드뱃지 + 사진 + 캡션 + EDIT/HISTORY + 파도타기 버튼 | `MinihomepyService.get_profile`(nickname/mood/status_message, 신규) |
| 통계 바 | 다이어리/방명록/사진첩 개수 | `diary_count()`(신규)·`guestbook.count()`(신규)·사진첩은 미구현 스텁(0) |
| 뮤직 플레이어 | 재생목록 위젯 | 정적 자리표시자(실제 재생 기능 없음, 범위 밖) |
| What Friends say | 친구 댓글 요약 | 방명록 중 마스킹 안 된 최근 항목 상위 2개 |
| Miniroom | 픽셀아트 방 일러스트 | **자리표시자**(이모지) — 실 일러스트 자산 없음, 아래 경계 참고 |
| 다이어리 | viewer가 조회 가능한 게시글만 | minihomepy AC-2~AC-4 |
| 방명록 | 목록(비밀글 마스킹)·주인 답글·작성 폼 | guestbook AC-1·AC-4·AC-5 |
| 우측 탭 | 홈/사진첩/다이어리/방명록 | 홈=현재 페이지, 다이어리/방명록=앵커 스크롤, 사진첩=비활성(미구현) |

## 라우트 (기존과 동일, 변경 없음)
- `GET /` : 데모 시드 사용자 목록(링크)
- `GET /minihomepy/<owner>?viewer=<viewer>` : 페이지 렌더(뷰어 방문 카운트 반영)
- `POST /minihomepy/<owner>/guestbook` : 방명록 작성 후 같은 페이지로 리다이렉트

## 보안 고려
- 프로필(닉네임·무드·상태메시지)·다이어리·방명록 콘텐츠는 전부 `html.escape`로
  이스케이프한다(XSS 방지). 새로 추가된 프로필 필드도 동일 규칙 적용.

## 알려진 자산 경계 (정직하게 기록)
- **Miniroom 픽셀아트, 프로필 사진**: 레퍼런스의 실제 일러스트/사진 자산이 없고, 이 환경에는
  이미지 생성·크롭 도구도 없다. 이모지 기반 자리표시자로 레이아웃과 색감만 재현했다.
- **뮤직 플레이어**: 실제 재생 로직 없음(정적 위젯).
- **브라우저 픽셀 비교 없음**: Playwright/브라우저 비가용이라 실행 가능한 서버 기동 + curl
  스모크 + 렌더 함수 유닛테스트로 대체 검증했다.

## 검증 매핑
| 항목 | 테스트 |
| --- | --- |
| 통계 바(TODAY/TOTAL) | `tests/test_minihomepy_screen.py::test_render_stats_bar` |
| 프로필 사이드바(무드/캡션/파도타기) | `tests/test_minihomepy_screen.py::test_render_profile_sidebar` |
| 다이어리 공개범위별 렌더 | `tests/test_minihomepy_screen.py::test_render_diary_visibility` |
| 방명록 마스킹·답글 렌더 | `tests/test_minihomepy_screen.py::test_render_guestbook` |
| What Friends say(마스킹 제외) | `tests/test_minihomepy_screen.py::test_render_friends_say_hides_masked_entries` |
| 탭 네비게이션(active/disabled) | `tests/test_minihomepy_screen.py::test_render_nav_tabs_marks_active` |
| XSS 이스케이프(프로필 포함) | `tests/test_minihomepy_screen.py::test_render_escapes_user_content` |
| 페이지 조립 | `tests/test_minihomepy_screen.py::test_render_page_assembles_sections` |
| 실행 가능한 웹서버 | 수동 스모크: `python3 -m server.web.app` 기동 후 curl (04_verify 기록) |
