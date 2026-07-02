package kr.elice.library.springboot;

import kr.elice.library.api.LoanService;
import kr.elice.library.domain.LibraryException;
import kr.elice.library.domain.Loan;
import kr.elice.library.platform.CatalogRouter;
import kr.elice.library.store.LoanStore;
import org.springframework.stereotype.Service;

/**
 * 신규 대출 모듈입니다. 도서·회원은 직접 참조하지 않고 {@link CatalogRouter} 를 통해
 * 활성 구현(레거시 또는 신규)을 받아 호출합니다. 전환 중간 상태에서도 항상 올바른
 * 구현을 바라보기 위함입니다.
 *
 * <p>업무 규칙은 레거시와 동일합니다. AC-1 은 한 회원이 동시에 5권을 넘겨 빌릴 수
 * 없다는 것이고, AC-2 는 연체 중인 회원은 새로 빌릴 수 없다는 것입니다.</p>
 */
@Service
public class NewLoanService implements LoanService {

    private static final int LIMIT = 5;

    private final CatalogRouter router;
    private final LoanStore store;

    public NewLoanService(CatalogRouter router, LoanStore store) {
        this.router = router;
        this.store = store;
    }

    @Override
    public Loan borrow(String memberId, String bookId, int daysUntilDue) {
        router.members().get(memberId);  // 존재 검증 (없으면 NOT_FOUND)
        router.books().get(bookId);
        if (activeCount(memberId) >= LIMIT) {                       // AC-1
            throw new LibraryException(LibraryException.Code.LOAN_LIMIT_EXCEEDED,
                    "대출 한도 " + LIMIT + "권을 초과했습니다.");
        }
        if (hasOverdue(memberId)) {                                 // AC-2
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
