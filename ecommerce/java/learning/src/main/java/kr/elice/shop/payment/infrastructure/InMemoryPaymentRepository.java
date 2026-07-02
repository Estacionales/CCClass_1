package kr.elice.shop.payment.infrastructure;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import kr.elice.shop.payment.domain.Payment;
import kr.elice.shop.payment.domain.PaymentRepository;
import org.springframework.stereotype.Repository;

@Repository
public class InMemoryPaymentRepository implements PaymentRepository {

    private final Map<String, Payment> store = new ConcurrentHashMap<>();
    private final Map<String, String> byOrderId = new ConcurrentHashMap<>();

    @Override
    public Payment save(Payment payment) {
        store.put(payment.id(), payment);
        byOrderId.put(payment.orderId(), payment.id());
        return payment;
    }

    @Override
    public Optional<Payment> findById(String id) {
        return Optional.ofNullable(store.get(id));
    }

    @Override
    public Optional<Payment> findByOrderId(String orderId) {
        String id = byOrderId.get(orderId);
        return id == null ? Optional.empty() : Optional.ofNullable(store.get(id));
    }
}
