package kr.elice.library.legacy;

import kr.elice.library.api.MemberService;
import kr.elice.library.domain.LibraryException;
import kr.elice.library.domain.Member;
import kr.elice.library.store.MemberStore;
import org.springframework.stereotype.Service;

/** 레거시 회원 모듈입니다. 공유 MemberStore 를 사용합니다. */
@Service
public class LegacyMemberService implements MemberService {

    private final MemberStore store;

    public LegacyMemberService(MemberStore store) {
        this.store = store;
    }

    @Override
    public Member register(String name) {
        return store.save(new Member(store.nextId(), name));
    }

    @Override
    public Member get(String id) {
        return store.find(id).orElseThrow(() ->
                new LibraryException(LibraryException.Code.NOT_FOUND, "회원을 찾을 수 없습니다: " + id));
    }
}
