package kr.elice.library.store;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import kr.elice.library.domain.Member;
import org.springframework.stereotype.Component;

/** 회원 공유 저장소입니다. 레거시·신규 구현이 같은 회원 데이터를 봅니다. */
@Component
public class MemberStore {

    private final Map<String, Member> rows = new ConcurrentHashMap<>();
    private final AtomicLong seq = new AtomicLong(0);

    public String nextId() {
        return "member_" + seq.incrementAndGet();
    }

    public Member save(Member member) {
        rows.put(member.id(), member);
        return member;
    }

    public Optional<Member> find(String id) {
        return Optional.ofNullable(rows.get(id));
    }
}
