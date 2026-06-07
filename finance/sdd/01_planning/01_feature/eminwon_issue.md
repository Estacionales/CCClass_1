# 전자민원 자동 발급 · Acceptance Criteria (EARS)

> 01_planning — 요구사항 원문(`00_sources/02_requirements/mylink-전자민원.md`)을
> 검증 가능한 EARS 수용기준으로 정제한다. 이 다섯 줄이 곧 가드레일이다.

## Acceptance Criteria

**AC-1** While 사용자가 마이데이터 동의를 완료했을 때, when 전자민원 발급을 요청하면,
the system shall 자격 규칙으로 서류 목록을 산출하고 해당 연계기관에서 수집한다.

**AC-2** When 연계기관 응답이 3초 내 미도착이면, the system shall 재시도 3회 →
서킷브레이커 → 대체 경로로 graceful degradation 한다. (회복력)

**AC-3** The 발급 판단은 shall 근거 규정 다단계 조회로 '민원 → 필요서류 → 근거규정 → 예외'를
추론하고, 근거 문서를 반드시 인용한다. 자격 미달이면 발급을 거부한다. (근거 인용·가드레일)

**AC-4** When 발급/정산 배치가 재실행되면, the system shall 멱등성을 보장해
중복 발급/정산을 만들지 않는다.

**AC-5** When 사용자가 동의를 철회하면, the system shall 처리를 중단·파기하고
동의 원장에 기록한다.

## 검증 매핑 (각 AC → 테스트)

| AC | 검증 테스트 (proof 게이트) |
| --- | --- |
| AC-1 | `tests/test_ac1_issue.py` |
| AC-2 | `tests/test_ac2_resilience.py` |
| AC-3 | `tests/test_ac3_citation.py` + `99_toolchain/01_automation/run_citation_check.py` |
| AC-4 | `tests/test_ac4_idempotent.py` |
| AC-5 | `tests/test_ac5_withdrawal.py` |
| 회귀 | `tests/test_regression.py` |
