# 회원가입 OTP · todos + 실행 계획

## Scope
이메일 OTP 회원가입 한 기능을 발급·검증·만료·잠금·멱등 + 화면 parity까지 구현·검증.

## Acceptance Criteria
- AC-1~AC-6 (`sdd/01_planning/01_feature/auth_feature_spec.md`) 전부 테스트 통과.
- 회귀(로그인) green. proof 게이트 exit 0 = 완료.

## Execution Checklist (비중첩)
- [x] T1 @backend-dev  OTP 발급·검증·만료·잠금 (`contexts/auth/otp.py`)
- [x] T2 @backend-dev  가입 + 멱등 (`contexts/auth/signup.py`)
- [x] T3 @frontend-dev OTP 입력 화면 (`contexts/auth/screens.py`)
- [x] T4 @test-dev     proof 게이트 + UI parity (`tests/`, `run_ui_parity.py`)

## Regression Scope
- direct: 가입·OTP 흐름
- shared: 로그인(`contexts/auth/login.py`), 계정 저장소
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Validation
- `python3 proof/run_proof.py` → 10/10 PASS
- `python3 sdd/99_toolchain/01_automation/run_ui_parity.py` → ui_parity 1/1
