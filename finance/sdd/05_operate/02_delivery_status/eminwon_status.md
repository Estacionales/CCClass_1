# 전자민원 발급 · 현재 딜리버리 상태

| 항목 | 상태 |
| --- | --- |
| 현재 baseline | 동의 후 전자민원 자동 발급 (AC-1~AC-5 구현 완료) |
| proof 게이트 | PASS · 14/14 (`tmp/proof-results.json`) |
| 근거 인용 | citation_exactness 3/3 |
| 배포 환경 | DEV(로컬 인프로세스 데모) — PROD 미배포 |
| 모니터링 baseline | proof 게이트 + 근거 인용 검사 재실행 |

## 규제 산출물(데모 산출)
- 동의 원장: `consent_ledger` append-only 이력 (부여·철회)
- 근거 인용 로그: `run_citation_check.py` 출력
- DPIA/모델 카드: 대규모 운영 시 사이드카로 자동 산출(데모 범위 밖, 형식만 제시)

## 잔여 위험
- 실 연계기관 통신·성능 SLA는 미검증 (데모 경계).
