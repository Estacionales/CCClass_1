# 회원가입 OTP · 검증 (retained) — 회귀 4분면

> proof: `python3 proof/run_proof.py` → 10/10 PASS (exit 0).

| 분면 | 검증 대상 | 수용기준 | 결과 |
| --- | --- | --- | --- |
| 기능 | OTP 발급→검증→가입 | AC-1·AC-2 | PASS |
| 보안 | 5회 오입력 잠금 / TTL 만료 | AC-3·AC-4 | PASS |
| 멱등 | 재요청 시 계정 중복 0 | AC-5 | PASS · replay |
| 화면 | signup_otp 스냅샷 일치 | AC-6 | PASS · ui_parity 1/1 |
| 회귀 | 기존 로그인 무손상 | shared | PASS |

## Residual Risk
- 실 브라우저(Playwright) 픽셀 비교·compose 부팅은 데모 범위 밖 — HTML parity로 대체.
- 메일 발송·실 OTP 채널은 미구현(주입 OTP로 대체).
