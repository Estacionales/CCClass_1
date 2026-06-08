package kr.elice.library.platform;

import java.util.Map;
import kr.elice.library.api.BookService;
import kr.elice.library.api.MemberService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * 도서·회원 모듈의 활성 구현을 골라 주는 앞단 라우터입니다.
 *
 * <p>migration.properties 의 module.books / module.members 값에 따라 legacy 또는
 * new 빈을 선택합니다. 빈 이름 규약은 "{legacy|new}{Book|Member}Service" 입니다.
 * 신규 구현이 아직 없는데 new 로 지정되면, 무엇을 만들어야 하는지 알려 주며 멈춥니다.
 * 대출 모듈의 신규 구현도 이 라우터로 도서·회원의 활성 구현을 받아 호출합니다.</p>
 */
@Component
public class CatalogRouter {

    private final Map<String, BookService> bookImpls;
    private final Map<String, MemberService> memberImpls;
    private final String booksMode;
    private final String membersMode;

    public CatalogRouter(Map<String, BookService> bookImpls,
                         Map<String, MemberService> memberImpls,
                         @Value("${module.books}") String booksMode,
                         @Value("${module.members}") String membersMode) {
        this.bookImpls = bookImpls;
        this.memberImpls = memberImpls;
        this.booksMode = booksMode;
        this.membersMode = membersMode;
    }

    public BookService books() {
        return Routing.pick(bookImpls, booksMode, "Book");
    }

    public MemberService members() {
        return Routing.pick(memberImpls, membersMode, "Member");
    }
}
