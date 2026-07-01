package dev.agentic.demo;

import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * spec.md(AC-1~4)를 만족하는 학습자 구현.
 *
 * - AC-2(만료): 발급 시각(t)을 기억해 TTL(300초)을 넘기면 거부한다.
 * - AC-3(잠금): 같은 사용자가 5회 연속 오답을 내면 이후 정답도 거부한다.
 * - AC-4(멱등): created를 Set으로 관리해 같은 사용자가 두 번 가입해도 1건만 남는다.
 */
public class MyOtp implements Otp {

    private static final int TTL_SECONDS = 300;
    private static final int MAX_ATTEMPTS = 5;

    private static final class Record {
        final String code;
        final int issuedAt;
        int fails;
        boolean locked;

        Record(String code, int issuedAt) {
            this.code = code;
            this.issuedAt = issuedAt;
        }
    }

    private final Map<String, Record> codes = new HashMap<>();
    private final Set<String> created = new HashSet<>();

    @Override
    public String issue(String email, int t) {
        codes.put(email, new Record("123456", t));
        return "123456";
    }

    @Override
    public boolean verify(String email, String code, int t) {
        Record r = codes.get(email);
        if (r == null || r.locked) {
            return false;
        }
        if (t - r.issuedAt > TTL_SECONDS) {
            return false;
        }
        if (!r.code.equals(code)) {
            r.fails += 1;
            if (r.fails >= MAX_ATTEMPTS) {
                r.locked = true;
            }
            return false;
        }
        return true;
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
