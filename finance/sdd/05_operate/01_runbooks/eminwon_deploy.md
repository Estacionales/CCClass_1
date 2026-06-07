# 전자민원 발급 · DEV 배포 runbook

> 05_operate — 배포·운영 절차를 박제한다. main push = DEV 배포 트리거.
> 망분리 운영계(PROD)는 본 데모 경계 밖.

## 배포 절차 (DEV)
1. proof 게이트 green 확인: `python3 proof/run_proof.py` → exit 0
2. current-state 갱신 확인: `sdd/03_build`, `sdd/04_verify`
3. main 커밋·푸시 (= DEV 배포 트리거)
   ```
   git commit -m "feat(eminwon): 동의 후 전자민원 자동발급 + 회복력·멱등"
   git push origin main
   ```
4. (CI) deploy-dev: build → DEV 배포 → smoke `POST /api/v1/eminwon/issue`
5. 규제 리포트 사이드카: 동의원장 export · DPIA 초안 · 모델·데이터 문서

## 게이트
- DEV 완료 기준 = proof green + smoke 통과.
- PROD 승격은 본 데모 범위 밖 (망분리 운영계 미접근).

## 롤백 트리거
- smoke 실패 또는 회귀 4분면 중 하나라도 fail → 직전 main으로 롤백.
