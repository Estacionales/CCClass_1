package kr.elice.library.api;

import kr.elice.library.domain.Member;

/**
 * 회원 모듈 계약입니다. legacy 와 springboot 두 구현이 이 인터페이스를 똑같이 만족합니다.
 */
public interface MemberService {

    Member register(String name);

    Member get(String id);
}
