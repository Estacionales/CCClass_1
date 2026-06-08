package kr.elice.library.springboot;

import kr.elice.library.api.LoanService;
import kr.elice.library.domain.LibraryException;
import kr.elice.library.domain.Loan;
import kr.elice.library.platform.CatalogRouter;
import kr.elice.library.store.LoanStore;
import org.springframework.stereotype.Service;

/**
 * 신규 대출 모듈(Spring Boot)입니다. 대출 한도(AC-1)와 연체 거부(AC-2)를 그대로 지킵니다.
 *
 * <p>대출은 도서·회원을 함께 사용하므로, 두 모듈의 활성 구현을 {@link CatalogRouter}
 * 로 받아 호출합니다. 그래서 도서·회원이 아직 레거시여도 신규 대출이 정상 동작합니다.
 * 대출 데이터는 공유 LoanStore 를 사용해 전환 전후 연속성을 지킵니다.</p>
 */
@Service
public class NewLoanService implements LoanService {

    private static final int LIMIT = 5;

    private final CatalogRouter catalog;
    private final LoanStore store;

    public NewLoanService(CatalogRouter catalog, LoanStore store) {
        this.catalog = catalog;
        this.store = store;
    }

    @Override
    public Loan borrow(String memberId, String bookId, int daysUntilDue) {
        catalog.members().get(memberId);  // 활성 회원 모듈로 존재 검증
        catalog.books().get(bookId);       // 활성 도서 모듈로 존재 검증
        if (activeCount(memberId) >= LIMIT) {                        // AC-1
            throw new LibraryException(LibraryException.Code.LOAN_LIMIT_EXCEEDED,
                    "대출 한도 " + LIMIT + "권을 초과했습니다.");
        }
        if (hasOverdue(memberId)) {                                  // AC-2
            throw new LibraryException(LibraryException.Code.OVERDUE_EXISTS,
                    "연체 중인 대출이 있어 새로 빌릴 수 없습니다.");
        }
        return store.save(new Loan(store.nextId(), memberId, bookId, daysUntilDue));
    }

    @Override
    public void giveBack(String loanId) {
        Loan loan = store.find(loanId).orElseThrow(() ->
                new LibraryException(LibraryException.Code.NOT_FOUND, "대출을 찾을 수 없습니다: " + loanId));
        loan.markReturned();
    }

    @Override
    public int activeCount(String memberId) {
        return store.activeByMember(memberId).size();
    }

    @Override
    public boolean hasOverdue(String memberId) {
        return store.activeByMember(memberId).stream().anyMatch(Loan::isOverdue);
    }
}
