# MyLink 금융·공공 데모 타깃 (S13)

> 강의 13강 데모용 **가상** 금융·공공 서비스. 실재 기관·시스템·개인정보·실명 없음.
> agentic-dev 하네스(`.claude/skills/sdd`)를 적용해 SDD 워크플로우를 실제로 관통한 결과.

## 무엇인가
"동의 완료 후 전자민원 자동 발급" 한 기능을, 대규모·고규제 제약(회복력·근거인용·멱등·
동의철회)과 함께 end-to-end로 구현하고 결정적 proof 게이트로 증명한 최소 실동작 repo.

## 실행
```bash
pip install -r requirements.txt          # pytest
python3 -m compileall -q server          # build
python3 proof/run_proof.py               # proof  → 14/14 PASS, tmp/proof-results.json
python3 sdd/99_toolchain/01_automation/run_citation_check.py --feature eminwon  # verify_dev → 3/3
```

(또는 contract.json 의 `commands.build` / `commands.proof` / `commands.verify_dev` 그대로.)

## 구조
- `server/` — 도메인 구현 (eminwon·settlement·advisory·gw 어댑터·shared 계약)
- `tests/` — proof 게이트 = AC-1~AC-5 + 회귀 (14 케이스)
- `sdd/` — SDD 5단계 산출물 (00_sources → 01_planning → 02_plan → 03_build → 04_verify → 05_operate → 99_toolchain)
- `.agentic-dev/contract.json` — build/proof/deploy_dev/verify_dev 명령
- `.claude/skills/sdd`, `.codex/skills/sdd` — 적용된 SDD 스킬

## AC ↔ 코드 ↔ 테스트
| AC | 구현 | 테스트 |
| --- | --- | --- |
| AC-1 동의→발급 | `contexts/eminwon/issue_svc.py` | `test_ac1_issue.py` |
| AC-2 회복력 | `integration/adapters/gw/base_adapter.py` | `test_ac2_resilience.py` |
| AC-3 근거인용·가드레일 | `contexts/advisory/citation.py`·`shared/rules.py` | `test_ac3_citation.py` |
| AC-4 멱등 | `contexts/eminwon/idem.py`·`contexts/settlement/batch.py` | `test_ac4_idempotent.py` |
| AC-5 동의철회 | `shared/consent_ledger.py`·`issue_svc.handle_withdrawal` | `test_ac5_withdrawal.py` |
| 회귀 | shared surface | `test_regression.py` |
