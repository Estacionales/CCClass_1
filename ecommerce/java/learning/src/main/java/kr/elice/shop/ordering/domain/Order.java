package kr.elice.shop.ordering.domain;

import java.util.List;
import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import kr.elice.shop.shared.Money;

public class Order {

    private final String id;
    private final List<OrderLine> lines;
    private final List<String> reservationIds;
    private final Money totalAmount;
    private OrderStatus status;
    private String paymentId;

    private Order(String id, List<OrderLine> lines, List<String> reservationIds, Money totalAmount) {
        this.id = id;
        this.lines = lines;
        this.reservationIds = reservationIds;
        this.totalAmount = totalAmount;
        this.status = OrderStatus.CREATED;
    }

    public static Order create(String id, List<OrderLine> lines, List<String> reservationIds) {
        Money total = lines.stream()
                .map(OrderLine::lineTotal)
                .reduce(Money.won(0), Money::plus);
        if (!total.isPositive()) {
            throw new DomainException(ErrorCode.INVALID_AMOUNT, "주문 총액은 0원보다 커야 합니다.");
        }
        return new Order(id, lines, reservationIds, total);
    }

    public void markPaid(String paymentId) {
        requireStatus(OrderStatus.CREATED);
        this.paymentId = paymentId;
        this.status = OrderStatus.PAID;
    }

    public void fulfill() {
        if (status != OrderStatus.PAID) {
            throw new DomainException(ErrorCode.PAYMENT_REQUIRED, "결제가 완료되어야 이행할 수 있습니다.");
        }
        this.status = OrderStatus.FULFILLED;
    }

    public boolean cancel() {
        if (status == OrderStatus.FULFILLED || status == OrderStatus.CANCELLED) {
            throw new DomainException(ErrorCode.INVALID_STATE_TRANSITION, "이행 완료되었거나 이미 취소된 주문은 취소할 수 없습니다.");
        }
        boolean requiresRefund = status == OrderStatus.PAID;
        this.status = OrderStatus.CANCELLED;
        return requiresRefund;
    }

    private void requireStatus(OrderStatus expected) {
        if (status != expected) {
            throw new DomainException(ErrorCode.INVALID_STATE_TRANSITION, "허용되지 않는 상태 전환입니다.");
        }
    }

    public String id() {
        return id;
    }

    public List<OrderLine> lines() {
        return lines;
    }

    public List<String> reservationIds() {
        return reservationIds;
    }

    public Money totalAmount() {
        return totalAmount;
    }

    public OrderStatus status() {
        return status;
    }

    public String paymentId() {
        return paymentId;
    }
}
