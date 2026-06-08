package kr.elice.library.platform;

import java.util.Map;
import kr.elice.library.api.LoanService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * 대출 모듈의 활성 구현을 골라 주는 앞단 라우터입니다.
 *
 * <p>도서·회원과 분리한 이유는 순환 의존을 피하기 위함입니다. 신규 대출 구현은
 * 도서·회원의 활성 구현을 {@link CatalogRouter} 로 받으므로, 대출 라우터가 대출
 * 구현만 책임지면 대출 구현이 다시 이 라우터를 참조하지 않아 순환이 생기지 않습니다.</p>
 */
@Component
public class LoanRouter {

    private final Map<String, LoanService> loanImpls;
    private final String loansMode;

    public LoanRouter(Map<String, LoanService> loanImpls,
                      @Value("${module.loans}") String loansMode) {
        this.loanImpls = loanImpls;
        this.loansMode = loansMode;
    }

    public LoanService loans() {
        return Routing.pick(loanImpls, loansMode, "Loan");
    }
}
