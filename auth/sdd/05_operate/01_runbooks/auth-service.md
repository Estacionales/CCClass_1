# auth-service · 운영 runbook

> 절차·임계치·롤백·감사를 한 문서에. main push = DEV 배포 트리거.
> compose/운영계(PROD)는 본 데모 경계 밖.

## 배포 절차 (DEV)
1. proof green: `python3 proof/run_proof.py` → exit 0
2. UI parity: `python3 sdd/99_toolchain/01_automation/run_ui_parity.py` → 1/1
3. main 커밋·푸시 (= DEV 배포 트리거)
4. (CI) deploy-dev: build → DEV → smoke (가입 happy-path)

## 임계치·롤백
- 트리거: smoke 실패 또는 회귀 4분면 중 하나라도 fail.
- 절차: 직전 main으로 롤백 후 delivery_status 갱신.

## 감사
- OTP 잠금/만료 이벤트, 가입 멱등 키는 로그로 남긴다(데모: 인메모리).
