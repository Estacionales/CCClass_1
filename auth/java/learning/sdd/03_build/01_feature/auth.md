# 회원가입 OTP · current-state

> 03_build: Overwrite Rule(지금 상태 1벌).

## Absorbed Planning
- `01_planning/01_feature/auth_feature_spec.md` (AC-1~AC-6)
- `02_plan/01_feature/auth_todos.md` (T1~T4)

## Runtime Assembly
- `AuthController` → `POST /auth/otp/issue` → `OtpService.issue`
- `AuthController` → `POST /auth/signup` → `SignupService.signup` → `OtpService.verify` → 통과 시 `AccountRepository.save`(멱등)
- `AuthController` → `POST /auth/login` → `LoginService.login`(회귀 대상)

## Modules
| 모듈 | 책임 | AC |
| --- | --- | --- |
| `service/OtpService.java` | OTP 발급·검증·만료·잠금 | 1·3·4 |
| `service/SignupService.java` | 가입 + 멱등 | 2·5 |
| `service/IdempotencyStore.java` | idempotency_key로 중복 가입 차단 | 5 |
| `repository/AccountRepository.java` | 인메모리 계정 저장소 | - |
| `service/LoginService.java` | 기존 로그인(회귀) | - |
| `controller/AuthController.java` | otp/issue·signup·login 엔드포인트 | 1·2·3·4·5 |
| `controller/ApiExceptionHandler.java` | 입력 검증 실패 → 400 | - |

## Current Behavior
가입 요청(email+code) → `OtpService.verify`(TTL·잠금 판정) → 통과 시 계정 생성(idempotency_key로 중복 차단).
AC-6(화면 parity)은 REST 타깃이라 `ContractParityTest`의 응답 계약 정합으로 대체했다(HTML 화면 없음).
