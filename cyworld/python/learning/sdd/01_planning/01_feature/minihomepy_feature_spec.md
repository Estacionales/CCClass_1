# 미니홈피(HOMEPY) · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 원문: `sdd/00_sources/02_requirements/minihomepy.md`
> 의존: 일촌공개 접근제어는 [[chon_feature_spec]]의 일촌 관계 조회에, 스킨/BGM 적용은
> [[acorn_feature_spec]]의 인벤토리 조회에 의존한다.

**AC-1** When 사용자가 회원가입을 완료하면, the system shall 해당 사용자 소유의 미니홈피를
자동 생성한다.

**AC-2** When 다이어리 게시글을 작성하면서 공개범위(전체공개·일촌공개·비공개)를 지정하면,
the system shall 해당 공개범위로 게시글을 저장한다.

**AC-3** While 게시글 공개범위가 '비공개'일 때, when 작성자 본인이 아닌 사용자가 조회를
요청하면, the system shall 조회를 거부한다.

**AC-4** While 게시글 공개범위가 '일촌공개'일 때, when 작성자와 일촌 관계가 아닌 사용자가
조회를 요청하면, the system shall 조회를 거부한다.

**AC-5** When 본인이 아닌 사용자가 미니홈피를 방문하면, the system shall 방문자수를 1
증가시키고, 동일 방문자의 24시간 내 재방문은 중복 카운트하지 않는다.

**AC-6** When 사용자가 보유하지 않은 스킨·BGM을 미니홈피에 적용하려 하면, the system shall
적용을 거부한다.

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_minihomepy.py::test_signup_creates_homepy` |
| AC-2·AC-3 | `tests/test_minihomepy.py::test_diary_visibility_private` |
| AC-4 | `tests/test_minihomepy.py::test_diary_visibility_chon_only` (chon 컨텍스트 스텁 의존) |
| AC-5 | `tests/test_minihomepy.py::test_visitor_count_dedup_24h` |
| AC-6 | `tests/test_minihomepy.py::test_skin_bgm_requires_inventory` (acorn 컨텍스트 스텁 의존) |
| 회귀 | `tests/test_regression.py` (chon·acorn 공유 표면 포함) |
