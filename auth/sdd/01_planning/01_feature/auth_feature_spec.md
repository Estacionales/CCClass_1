# 회원가입 OTP · Acceptance Criteria (EARS)

> 01_planning — 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.

**AC-1** When 사용자가 회원가입을 요청하면, the system shall (email, purpose)에 묶인
6자리 OTP를 발급하고 TTL(300초)을 건다.

**AC-2** While OTP가 유효할 때, when 올바른 OTP가 입력되면,
the system shall 계정을 생성한다.

**AC-3** When OTP를 5회 연속 틀리면, the system shall 해당 OTP를 잠근다.

**AC-4** When OTP TTL(300초)이 지나면, the system shall 검증을 만료로 거부한다.

**AC-5** When 같은 사용자의 가입이 재요청되면, the system shall 멱등성을 보장해
계정을 중복 생성하지 않는다.

**AC-6(화면)** The signup_otp 화면은 shall 승인된 디자인 스냅샷과 일치한다(UI parity).

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1·AC-2 | `tests/test_otp.py`, `tests/test_signup.py` |
| AC-3 | `tests/test_otp.py::test_otp_wrong_then_lock` |
| AC-4 | `tests/test_otp.py::test_otp_expiry` |
| AC-5 | `tests/test_signup.py::test_signup_idempotent` |
| AC-6 | `tests/test_screen_parity.py` + `99_toolchain/01_automation/run_ui_parity.py` |
| 회귀 | `tests/test_regression.py` |
