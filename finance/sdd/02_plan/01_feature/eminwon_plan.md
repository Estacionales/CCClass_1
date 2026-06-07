# 전자민원 자동 발급 · 실행 계획

## Scope
동의 완료 후 전자민원 서류 자동 발급 한 기능을, 회복력·근거인용·멱등·동의철회
제약과 함께 end-to-end로 구현하고 결정적 proof 게이트로 검증한다.

## Assumptions
- 연계기관 응답은 `responder(doc_code, attempt)` 콜러블로 주입(데모: 인프로세스).
- PII 없음 — 사용자 식별자는 불투명 문자열만 사용.
- DEV 배포는 로컬 인프로세스 스텁. 망분리 운영계는 접근하지 않는다.

## Acceptance Criteria
- AC-1~AC-5 (`sdd/01_planning/01_feature/eminwon_issue.md`)가 모두 테스트로 통과.
- 회귀 표면(자격검증·정산·원장)이 함께 green.
- proof 게이트(`python3 proof/run_proof.py`) exit 0 = 완료 기준.
- 근거 인용 정확성(`run_citation_check.py`) 만점.

## Execution Checklist
- [x] T1 오케스트레이션 + 멱등키
- [x] T2 어댑터 회복력(재시도·서킷·대체)
- [x] T3 정산 배치 멱등
- [x] T4 근거 인용 응답 + 가드레일
- [x] 회귀 범위 선정 및 테스트화 (`sdd/02_plan/10_test/regression_verification.md`)
- [x] proof 게이트 green

## Regression Scope
- direct: 발급 오케스트레이션 흐름
- shared: 자격검증(`rules`/`eligibility`), 정산 합계(`settlement`), 동의 원장 append
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Validation
- `python3 proof/run_proof.py` → 14/14 PASS (tmp/proof-results.json)
- `python3 sdd/99_toolchain/01_automation/run_citation_check.py` → citation_exactness 3/3
