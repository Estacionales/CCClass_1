# 전자민원 발급 · 검증 (retained): 회귀 4분면

> 04_verify: command-level 증거 없이 완료를 주장하지 않는다.
> proof: `python3 proof/run_proof.py` → 14/14 PASS (exit 0), `tmp/proof-results.json`.

## 회귀 4분면

| 분면 | 검증 대상 | 수용기준 | 결과 |
| --- | --- | --- | --- |
| 연계 | 기관 무응답 → 재시도3·서킷·대체경로 | AC-2 회복력 | PASS · attempts=3, fallback |
| 정산 | 발급 배치 재실행 시 중복 0건 | AC-4 멱등 | PASS · 재실행 2회 중복 0 |
| 상담 | 응답에 근거 규정 여러 단계 인용 | AC-3 근거인용 | PASS · citation 3/3 |
| 규제 | 동의 철회 → 처리중단·파기·원장기록 | AC-5 동의철회 | PASS · 원장 append |
| 회귀 | 기존 자격검증·정산 무손상 | shared surface | PASS · 14/14 green |

## 근거 인용 정확성 (AC-3)
`run_citation_check.py`: '있다'가 아니라 '맞다'(경로 일치)까지:
```
전입신고 ─필요서류→ 주민등록표 ─근거규정→ 전자정부법 §9 ─예외→ 세대주 동의
citation_exactness 3/3 · PASS · 자격 미달 시 발급 거부(refused)
```

## Residual Risk
- 성능/가용성(P99·99.95%)은 데모 범위 밖: 동작 정합성만 증명.
- 연계기관 응답은 주입 콜러블로 대체: 실 기관 통신은 미검증(데모 경계).
