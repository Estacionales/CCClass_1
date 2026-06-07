# -*- coding: utf-8 -*-
"""화면 렌더 — OTP 입력 화면. UI parity(스냅샷 일치)의 대상.

실제 강의 데모는 Playwright exactness gate로 픽셀 단위를 비교하지만,
이 환경(브라우저·compose 비가용)에서는 결정적 HTML 스냅샷 parity로 대체한다.
"""

SIGNUP_OTP_HTML = (
    '<main class="signup">'
    '<h1>인증번호 입력</h1>'
    '<p>이메일로 받은 6자리 인증번호를 입력하세요.</p>'
    '<input name="otp" inputmode="numeric" maxlength="6"/>'
    '<button type="submit">확인</button>'
    '</main>'
)

SCREENS = {"signup_otp": SIGNUP_OTP_HTML}


def render(screen):
    return SCREENS[screen]
