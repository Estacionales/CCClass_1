package kr.elice.shop.payment.application;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import kr.elice.shop.inventory.application.InventoryService;
import kr.elice.shop.ordering.application.OrderService;
import kr.elice.shop.ordering.domain.Order;
import kr.elice.shop.payment.domain.Payment;
import kr.elice.shop.payment.domain.PaymentGateway;
import kr.elice.shop.payment.domain.PaymentRepository;
import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import org.springframework.stereotype.Service;

@Service
public class PaymentService {

    private final PaymentRepository payments;
    private final PaymentGateway gateway;
    private final OrderService orders;
    private final InventoryService inventory;
    private final Map<String, String> idempotencyKeys = new ConcurrentHashMap<>();

    public PaymentService(
            PaymentRepository payments, PaymentGateway gateway, OrderService orders, InventoryService inventory) {
        this.payments = payments;
        this.gateway = gateway;
        this.orders = orders;
        this.inventory = inventory;
    }

    public Payment pay(String orderId, String method, String idempotencyKey) {
        if (idempotencyKey != null) {
            String existingId = idempotencyKeys.get(idempotencyKey);
            if (existingId != null) {
                return get(existingId);
            }
        }
        Order order = orders.get(orderId);
        String id = "pay_" + UUID.randomUUID().toString().replace("-", "").substring(0, 8);
        boolean approved = gateway.charge(orderId, order.totalAmount(), method);
        if (!approved) {
            payments.save(Payment.declined(id, orderId, order.totalAmount()));
            throw new DomainException(ErrorCode.PAYMENT_DECLINED, "결제가 거절되었습니다.");
        }

        Payment captured = Payment.captured(id, orderId, order.totalAmount());
        payments.save(captured);
        orders.markPaid(orderId, id);
        for (String reservationId : order.reservationIds()) {
            inventory.confirm(reservationId);
        }
        if (idempotencyKey != null) {
            idempotencyKeys.put(idempotencyKey, id);
        }
        return captured;
    }

    public Payment get(String id) {
        return payments.findById(id)
                .orElseThrow(() -> new DomainException(ErrorCode.NOT_FOUND, "결제를 찾을 수 없습니다: " + id));
    }

    public Payment refund(String id) {
        Payment payment = get(id);
        payment.refund();
        payments.save(payment);
        return payment;
    }

    public Payment refundByOrderId(String orderId) {
        Payment payment = payments.findByOrderId(orderId)
                .orElseThrow(() -> new DomainException(ErrorCode.NOT_FOUND, "결제 내역을 찾을 수 없습니다: " + orderId));
        payment.refund();
        payments.save(payment);
        return payment;
    }
}
