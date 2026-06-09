# 회원가입 OTP · todos + 실행 계획

- Owner: auth-team · Status: planned
- canonical: sdd/01_planning/01_feature/auth_feature_spec.md

---

## Scope

이메일 OTP 회원가입 기능 (발급·검증·만료·잠금·멱등·화면 parity)

---

## Acceptance Criteria

| Code  | 조건 (EARS) | 테스트 |
| ----- | ----------- | ------ |
| AC-1  | 회원가입 요청 시 (email, purpose) 묶인 6자리 OTP 발급 + TTL 300초 설정 | `test_otp.py` |
| AC-2  | 유효한 OTP 입력 시 계정 생성 완료 | `test_signup.py` |
| AC-3  | 5회 연속 오답 시 해당 OTP 잠금 | `test_otp.py::test_otp_wrong_then_lock` |
| AC-4  | TTL(300초) 경과 시 만료로 거부 | `test_otp.py::test_otp_expiry` |
| AC-5  | 동일 사용자 재가입 요청 시 멱등성 보장 — 계정 중복 생성 없음 | `test_signup.py::test_signup_idempotent` |
| AC-6  | signup_otp 화면이 승인된 디자인 스냅샷과 일치 | `test_screen_parity.py` |
| AC-R  | 기존 로그인 흐름 회귀 없음 | `test_regression.py` |

---

## Execution Checklist

### 1. OTP 발급 (`server/contexts/auth/otp.py`)
- [ ] `generate_otp(email, purpose)` — 6자리 숫자 생성, TTL=600초 설정
- [ ] 동일 (email, purpose) 재요청 시 기존 OTP 반환 (멱등)
- [ ] 발급 결과 반환: `{otp_id, our_code, expires_at}`

### 2. OTP 검증 (`server/contexts/auth/otp.py`)
- [ ] `verify_otp(otp_id, code)` — 코드 일치 여부 확인
- [ ] 실패 카운터 +1, 5회 도달 시 `status=locked` 전환
- [ ] TTL 초과 시 `status=expired` 반환
- [ ] 성공 시 `status=verified` 반환 후 1회성 소비 처리

### 3. 회원가입 플로우 (`server/contexts/auth/signup.py`)
- [ ] `request_signup(email)` — OTP 발급 호출 후 otp_id 반환
- [ ] `confirm_signup(email, otp_id, code)` — OTP 검증 후 계정 생성
- [ ] 멱등성: 이미 생성된 계정이면 기존 계정 반환 (중복 INSERT 없음)

### 4. 화면 parity (`sdd/04_verify/10_test/ui_parity/signup_otp.html`)
- [ ] 디자인 스냅샷(`signup_otp.html`) 기준으로 렌더링 확인
- [ ] `run_ui_parity.py` 실행 — diff 0 통과

### 5. 테스트 (`tests/`)
- [ ] `test_otp.py` — 발급·검증·만료·잠금 케이스 전체 통과
- [ ] `test_signup.py` — 정상 가입·멱등 케이스 전체 통과
- [ ] `test_screen_parity.py` — UI parity 통과
- [ ] `test_regression.py` — 기존 로그인 흐름 회귀 없음 확인

### 6. DEV 게이트
- [ ] 전체 테스트 스위트 green
- [ ] 스키마 drift 0 확인
- [ ] 롤백 조건 정의 (`sdd/05_operate/01_runbooks/auth-service.md` 업데이트)

---

## Latest Verification

- proof: 미실행
