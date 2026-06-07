# 99_toolchain: SDD 자동화

이 데모의 검증·인용 자동화 도구.

## run_citation_check.py
근거 인용 정확성(AC-3) 검사: '민원 → 필요서류 → 근거규정 → 예외' 경로와 인용이
일치하는지 자동 점수화한다.

```
python3 sdd/99_toolchain/01_automation/run_citation_check.py --feature eminwon
# → citation_exactness 3/3 · PASS (exit 0)
```

contract.json 의 `verify_dev` 가 이 스크립트를 가리킨다.

> 결정적 규칙 그래프(`server/shared/rules.py`)를 사용한다. GraphRAG가 아니라,
> 근거 규정 여러 단계 조회를 결정적으로 검증하는 도구다.
