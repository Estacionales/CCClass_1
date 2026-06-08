package kr.elice.library.domain;

/**
 * 도서관 도메인 규칙 위반 예외입니다. 대출 한도 초과·연체·미존재를 코드로 구분합니다.
 *
 * <p>이 규칙들이 곧 수용기준입니다. 레거시든 신규든 같은 규칙을 지켜야 하므로,
 * 두 구현 모두 같은 예외 코드를 던집니다.</p>
 */
public class LibraryException extends RuntimeException {

    public enum Code {
        LOAN_LIMIT_EXCEEDED,   // AC-1: 대출 한도 5권 초과
        OVERDUE_EXISTS,        // AC-2: 연체 보유 시 대출 거부
        NOT_FOUND
    }

    private final Code code;

    public LibraryException(Code code, String message) {
        super(message);
        this.code = code;
    }

    public Code code() {
        return code;
    }
}
