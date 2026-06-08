package kr.elice.library.domain;

/**
 * 대출 도메인입니다.
 *
 * <p>{@code daysUntilDue} 는 대출 시점에 정해지는 반납 기한입니다. 값이 음수이면
 * 이미 기한이 지난(연체) 대출을 뜻합니다. 데모에서는 시계 대신 이 값으로 연체를
 * 결정적으로 표현합니다. {@code returned} 가 false 인 대출만 활성으로 셉니다.</p>
 */
public class Loan {

    private final String id;
    private final String memberId;
    private final String bookId;
    private final int daysUntilDue;
    private boolean returned;

    public Loan(String id, String memberId, String bookId, int daysUntilDue) {
        this.id = id;
        this.memberId = memberId;
        this.bookId = bookId;
        this.daysUntilDue = daysUntilDue;
        this.returned = false;
    }

    public boolean isActive() {
        return !returned;
    }

    public boolean isOverdue() {
        return !returned && daysUntilDue < 0;
    }

    public void markReturned() {
        this.returned = true;
    }

    public String id() {
        return id;
    }

    public String memberId() {
        return memberId;
    }

    public String bookId() {
        return bookId;
    }

    public int daysUntilDue() {
        return daysUntilDue;
    }

    public boolean returned() {
        return returned;
    }
}
