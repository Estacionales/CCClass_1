package kr.elice.shop.payment.domain;

import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import kr.elice.shop.shared.Money;

public class Payment {

    private final String id;
    private final String orderId;
    private final Money amount;
    private PaymentStatus status;

    private Payment(String id, String orderId, Money amount, PaymentStatus status) {
        this.id = id;
        this.orderId = orderId;
        this.amount = amount;
        this.status = status;
    }

    public static Payment captured(String id, String orderId, Money amount) {
        return new Payment(id, orderId, amount, PaymentStatus.CAPTURED);
    }

    public static Payment declined(String id, String orderId, Money amount) {
        return new Payment(id, orderId, amount, PaymentStatus.DECLINED);
    }

    public void refund() {
        if (status != PaymentStatus.CAPTURED) {
            throw new DomainException(ErrorCode.REFUND_NOT_ALLOWED, "캡처되지 않은 결제는 환불할 수 없습니다.");
        }
        this.status = PaymentStatus.REFUNDED;
    }

    public String id() {
        return id;
    }

    public String orderId() {
        return orderId;
    }

    public Money amount() {
        return amount;
    }

    public PaymentStatus status() {
        return status;
    }
}
