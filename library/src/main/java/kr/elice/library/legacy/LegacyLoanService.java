package kr.elice.library.legacy;

import kr.elice.library.api.LoanService;
import kr.elice.library.domain.LibraryException;
import kr.elice.library.domain.Loan;
import kr.elice.library.store.LoanStore;
import org.springframework.stereotype.Service;

/**
 * 레거시 대출 모듈입니다. 모놀리식답게 도서·회원 모듈을 직접 들고 사용합니다.
 *
 * <p>업무 규칙 두 가지를 지킵니다. AC-1 은 한 회원이 동시에 5권을 넘겨 빌릴 수 없다는
 * 것이고, AC-2 는 연체 중인 회원은 새로 빌릴 수 없다는 것입니다. 도서·회원 조회는
 * 레거시 모듈을 직접 부르지만, 저장소가 공유라 전환 중에도 같은 데이터를 봅니다.</p>
 */
@Service
public class LegacyLoanService implements LoanService {

    private static final int LIMIT = 5;

    private final LegacyBookService books;
    private final LegacyMemberService members;
    private final LoanStore store;

    public LegacyLoanService(LegacyBookService books, LegacyMemberService members, LoanStore store) {
        this.books = books;
        this.members = members;
        this.store = store;
    }

    @Override
    public Loan borrow(String memberId, String bookId, int daysUntilDue) {
        members.get(memberId);  // 존재 검증 (없으면 NOT_FOUND)
        books.get(bookId);
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
