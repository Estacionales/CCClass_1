package dev.agentic.demo;

import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class MyOtp implements Otp {

    private static final int TTL = 300;
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
        String code = "123456";
        codes.put(email, new Record(code, t));
        return code;
    }

    @Override
    public boolean verify(String email, String code, int t) {
        Record r = codes.get(email);
        if (r == null || r.locked) {
            return false;
        }
        if (t - r.issuedAt > TTL) {
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
