# 회원가입 OTP · 검증 (retained): 회귀 4분면

> proof: `./gradlew test` → 10/10 PASS (exit 0). 근거: `tmp/proof-results.json`.

| 분면 | 검증 대상 | 수용기준 | 결과 |
| --- | --- | --- | --- |
| 기능 | OTP 발급→검증→가입 | AC-1·AC-2 | PASS (`OtpServiceTest`, `SignupFlowTest`) |
| 보안 | 5회 오입력 잠금 / TTL 만료 | AC-3·AC-4 | PASS (`OtpServiceTest`) |
| 멱등 | 재요청 시 계정 중복 0 | AC-5 | PASS · replay (`SignupFlowTest.signupIdempotent`) |
| 응답 계약(화면 parity 대체) | signup/otp 응답 필드 계약 | AC-6 | PASS (`ContractParityTest`) |
| 회귀 | 기존 로그인 무손상 | shared | PASS (`RegressionTest`) |

## Validation Commands
- `./gradlew test` → 10/10 PASS
- `./gradlew uiParity` → PASS (회귀 게이트 재실행)

## Residual Risk
- 실 브라우저(Playwright) 픽셀 비교는 데모 범위 밖: REST 응답 계약 정합으로 대체.
- 메일 발송·실 OTP 채널은 미구현(발급 API 응답에 code를 직접 포함하는 데모용 주입 방식).
