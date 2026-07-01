package com.datasense.auth.service;

import com.datasense.auth.domain.SignupResult;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;

/** 멱등 처리: idempotency_key로 중복 가입을 차단한다 (AC-5). */
@Component
public class IdempotencyStore {

    private final Map<String, SignupResult> seen = new ConcurrentHashMap<>();

    /** payload를 sha256으로 해싱해 멱등 키를 만든다. */
    public static String idempotencyKey(String email) {
        try {
            String raw = "{\"email\": \"" + email + "\"}";
            byte[] digest = MessageDigest.getInstance("SHA-256")
                    .digest(raw.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(digest);
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
    }

    /** key가 처음이면 fn을 실행해 저장하고 replay=false, 재요청이면 저장값과 replay=true. */
    public Issued issueOnce(String key, Supplier<SignupResult> fn) {
        SignupResult cached = seen.get(key);
        if (cached != null) {
            return new Issued(cached, true);
        }
        SignupResult result = fn.get();
        seen.put(key, result);
        return new Issued(result, false);
    }

    public record Issued(SignupResult result, boolean replay) {
    }
}
