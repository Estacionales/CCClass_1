# 회원가입 OTP · current-state

> 03_build — Overwrite Rule(지금 상태 1벌).

## Absorbed Planning
- `01_planning/01_feature/auth_feature_spec.md` (AC-1~AC-6)
- `02_plan/01_feature/auth_todos.md` (T1~T4)

## Runtime Assembly
- `SignupService.signup(email, code)` → `OTPService.verify` → 계정 생성(멱등)
- 화면: `screens.render("signup_otp")`

## Modules
| 모듈 | 책임 | AC |
| --- | --- | --- |
| `contexts/auth/otp.py` | OTP 발급·검증·만료·잠금 | 1·3·4 |
| `contexts/auth/signup.py` | 가입 + 멱등 | 2·5 |
| `contexts/auth/screens.py` | OTP 입력 화면 | 6 |
| `contexts/auth/login.py` | 기존 로그인(회귀) | — |
| `shared/idem.py` | idempotency_key | 5 |

## Current Behavior
가입 요청 → OTP 발급 → 검증(만료·잠금 처리) → 통과 시 계정 생성(중복 차단).
OTP 화면은 승인 스냅샷과 일치.
