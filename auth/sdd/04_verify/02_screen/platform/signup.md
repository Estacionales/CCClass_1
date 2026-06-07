# signup_otp 화면 · 검증 (retained)

- 캐노니컬 스냅샷: `sdd/04_verify/10_test/ui_parity/signup_otp.html`
- 게이트: `python3 sdd/99_toolchain/01_automation/run_ui_parity.py` → ui_parity 1/1 PASS
- 실 강의 데모는 Playwright exactness gate로 픽셀 비교; 본 환경은 결정적 HTML parity로 대체.

## Surface
- 요소: 제목('인증번호 입력'), 안내문, 6자리 입력(`maxlength="6"`), 확인 버튼.

## Residual Risk
- 실제 렌더 픽셀/반응형 레이아웃은 미검증(브라우저 비가용).
