package kr.elice.library.platform;

import kr.elice.library.domain.Loan;

/** 대출 응답 DTO 입니다. 도메인 Loan 을 외부에 노출할 형태로 고정합니다. */
public record LoanResponse(String id, String memberId, String bookId, int daysUntilDue,
        boolean returned) {

    public static LoanResponse from(Loan loan) {
        return new LoanResponse(loan.id(), loan.memberId(), loan.bookId(),
                loan.daysUntilDue(), loan.returned());
    }
}
