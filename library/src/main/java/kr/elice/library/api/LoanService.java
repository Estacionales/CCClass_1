package kr.elice.library.api;

import kr.elice.library.domain.Loan;

/**
 * 대출 모듈 계약입니다. 대출 한도(AC-1)와 연체 거부(AC-2) 규칙의 책임자입니다.
 *
 * <p>대출은 도서와 회원을 함께 사용합니다. 그래서 신규 구현은 도서·회원 모듈의
 * 활성 구현을 라우터로 받아 호출합니다. 어느 구현이 활성이든 같은 수용기준을 지킵니다.</p>
 */
public interface LoanService {

    /** 대출합니다. daysUntilDue 가 음수이면 이미 연체된(기한 지난) 대출을 뜻합니다. */
    Loan borrow(String memberId, String bookId, int daysUntilDue);

    void giveBack(String loanId);

    int activeCount(String memberId);

    boolean hasOverdue(String memberId);
}
