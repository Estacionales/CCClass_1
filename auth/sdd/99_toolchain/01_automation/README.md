# 99_toolchain — SDD 자동화

## run_ui_parity.py
OTP 화면 렌더를 캐노니컬 스냅샷(`sdd/04_verify/10_test/ui_parity/signup_otp.html`)과
대조하는 결정적 게이트.

```
python3 sdd/99_toolchain/01_automation/run_ui_parity.py
# → ui_parity 1/1 · PASS (exit 0)
```

contract.json 의 `verify_dev` 가 이 스크립트를 가리킨다.

> 실 강의에서는 Playwright exactness gate(`run_playwright_exactness.py`)가 이 자리에 온다.
> 본 데모 환경은 브라우저 비가용이라 HTML 스냅샷 parity로 대체했다.
