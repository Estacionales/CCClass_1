package dev.agentic.demo;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 학습자 구현 (시작점 · 바이브 라운드) — 명세 없이 'OTP 만들어줘'만 듣고 짠 전형적 결과입니다.
 *
 * 코드 일치만 보고 바로 가입시키므로 AC-1(정상)만 통과하고, 만료·잠금·멱등은 빠져
 * ./gradlew grade 가 보통 1/4 를 줍니다. spec.md(AC-1~4)를 읽고 이 클래스를 4/4로 고치는 것이
 * 이번 실습입니다. 막히면 complete/ 의 MyOtp 와 비교하세요.
 */
public class MyOtp implements Otp {

    private final Map<String, String> codes = new HashMap<>();
    private final List<String> created = new ArrayList<>(); // TODO(AC-4 멱등): Set 으로 바꿔 중복 가입을 막으세요

    @Override
    public String issue(String email, int t) {
        codes.put(email, "123456");
        return "123456";
    }

    @Override
    public boolean verify(String email, String code, int t) {
        // TODO(AC-2 만료): 발급 시각을 보관해 t - issuedAt > 300 이면 거부하세요.
        // TODO(AC-3 잠금): 오답 횟수를 세어 5회면 이후 정답도 거부하세요.
        // 코드 일치만 본다. 만료(t)도, 시도 횟수도 검사하지 않는다.
        String rec = codes.get(email);
        return rec != null && rec.equals(code);
    }

    @Override
    public boolean signup(String email, String code, int t) {
        if (!verify(email, code, t)) {
            return false;
        }
        created.add(email);
        return true;
    }

    @Override
    public Collection<String> created() {
        return created;
    }
}
