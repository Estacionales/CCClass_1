# 회원가입 OTP · todos + 실행 계획

## Scope
이메일 OTP 회원가입 한 기능을 발급·검증·만료·잠금·멱등까지 구현·검증.

## Acceptance Criteria
- AC-1~AC-5 (`sdd/01_planning/01_feature/auth_feature_spec.md`) 전부 테스트 통과.
- AC-6(화면 parity)은 REST 타깃이므로 응답 계약 정합(ContractParityTest)으로 대체.
- 회귀(로그인) green. proof 게이트 exit 0 = 완료.

## Execution Checklist (비중첩)
- [x] T1 @backend-dev  OTP 발급·검증·만료·잠금 (`src/main/java/com/datasense/auth/service/OtpService.java`)
- [x] T2 @backend-dev  가입 + 멱등 (`src/main/java/com/datasense/auth/service/SignupService.java`)
- [x] T3 @backend-dev  엔드포인트(otp/issue·signup·login) + 검증 실패 400 매핑
- [x] T4 @test-dev     proof 게이트 (`src/test/java/com/datasense/auth/` : OtpServiceTest·SignupFlowTest·RegressionTest·ContractParityTest)

## Regression Scope
- direct: 가입·OTP 흐름
- shared: 로그인(`src/main/java/com/datasense/auth/service/LoginService.java`), 계정 저장소(`AccountRepository`)
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Validation
- `./gradlew test` → JUnit 전체 PASS (`tmp/proof-results.json`)
- `./gradlew uiParity` → 회귀 게이트 재실행 PASS
