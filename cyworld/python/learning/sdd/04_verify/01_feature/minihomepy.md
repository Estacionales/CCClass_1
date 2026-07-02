# 미니홈피(HOMEPY) · 검증 (retained)

> proof: `python3 proof/run_proof.py` → 22/22 PASS (exit 0), 그 중 HOMEPY 6건.
> 실행: Python 3.14.6, `tmp/proof-results.json` (2026-07-02).

| 분면 | 검증 대상 | 수용기준 | 결과 |
| --- | --- | --- | --- |
| 기능 | 회원가입 훅 호출 시 미니홈피 생성 | AC-1 | PASS · `test_signup_creates_homepy` |
| 접근제어 | 비공개 게시글은 본인만 조회 | AC-2·AC-3 | PASS · `test_diary_visibility_private` |
| 기능 | 전체공개 게시글은 누구나 조회 | AC-2 | PASS · `test_diary_visibility_public` |
| 접근제어 | 일촌공개 게시글은 일촌 관계만 조회 (chon 컨텍스트 연동) | AC-4 | PASS · `test_diary_visibility_chon_only` |
| 기능 | 방문자수: 본인 제외, 24h 내 재방문 dedup | AC-5 | PASS · `test_visitor_count_dedup_24h` |
| 검증 | 스킨/BGM은 acorn 인벤토리 보유분만 적용 (acorn 컨텍스트 연동) | AC-6 | PASS · `test_skin_bgm_requires_inventory` |

## Regression
- CHON·ACORN 실제 서비스 인스턴스를 주입해 함께 실행 — 스텁이 아닌 실 컨텍스트 간 연동 검증.

## Residual Risk
- 없음(계획된 AC-1~AC-6 전부 구현·검증 완료). 다만 chon·acorn 저장소를 직접 참조하는 구조라,
  두 컨텍스트의 내부 자료구조(`is_chon`, `inventory`)가 바뀌면 이 모듈도 함께 회귀 검증 대상.
