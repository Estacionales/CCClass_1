# 전자민원 자동 발급 · Acceptance Criteria (EARS)

> 01_planning: 발주 요구사항정의서(`00_sources/02_requirements/MyLink_요구사항정의서_v1.0.docx`,
> 기능요구사항 SFR-001~005)를 검증 가능한 EARS 수용기준으로 정제한다. SFR → AC 1:1, 이 다섯 줄이 곧 가드레일이다.

## Acceptance Criteria

**AC-1** (← SFR-001) While 사용자가 마이데이터 동의를 완료했을 때, when 전자민원 발급을 요청하면,
the system shall 자격 규칙으로 서류 목록을 산출하고 해당 연계기관에서 수집한다.

**AC-2** (← SFR-002) When 연계기관 응답이 3초 내 미도착이면, the system shall 재시도 3회 →
서킷브레이커 → 대체 경로로 graceful degradation 한다. (회복력)

**AC-3** (← SFR-003) The 발급 판단은 shall 근거 규정 여러 단계 조회로 '민원 → 필요서류 → 근거규정 → 예외'를
추론하고, 근거 문서를 반드시 인용한다. 자격 미달이면 발급을 거부한다. (근거 인용·가드레일)

**AC-4** (← SFR-004) When 발급/정산 배치가 재실행되면, the system shall 멱등성을 보장해
중복 발급/정산을 만들지 않는다.

**AC-5** (← SFR-005) When 사용자가 동의를 철회하면, the system shall 처리를 중단·파기하고
동의 원장에 기록한다.

## 요구사항 추적 (SFR → AC → 테스트)

| 요구사항 (00_sources) | EARS (01_planning) | 검증 테스트 (proof 게이트) |
| --- | --- | --- |
| SFR-001 전자민원 자동 발급 | AC-1 | `tests/test_ac1_issue.py` |
| SFR-002 연계 회복력 | AC-2 | `tests/test_ac2_resilience.py` |
| SFR-003 근거 규정 조회·인용 | AC-3 | `tests/test_ac3_citation.py` + `99_toolchain/01_automation/run_citation_check.py` |
| SFR-004 발급·정산 멱등 | AC-4 | `tests/test_ac4_idempotent.py` |
| SFR-005 동의 철회·파기 | AC-5 | `tests/test_ac5_withdrawal.py` |
| (공유 표면) | 회귀 | `tests/test_regression.py` |

> 발주 요구사항정의서의 SFR이 EARS AC로 정제되고, 각 AC가 결정적 테스트로 검증됩니다: 
> `python3 proof/run_proof.py` 가 14개 전부 PASS면 요구사항이 코드까지 충족된 것입니다.
