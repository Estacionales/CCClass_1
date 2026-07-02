package kr.elice.shop.ordering.application;

import java.util.List;
import kr.elice.shop.ordering.domain.Order;
import kr.elice.shop.ordering.domain.OrderRepository;
import kr.elice.shop.ordering.domain.OrderStatus;
import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import kr.elice.shop.shared.Page;
import org.springframework.stereotype.Service;

@Service
public class OrderService {

    private final OrderRepository orders;

    public OrderService(OrderRepository orders) {
        this.orders = orders;
    }

    public Order get(String id) {
        return orders.findById(id)
                .orElseThrow(() -> new DomainException(ErrorCode.NOT_FOUND, "주문을 찾을 수 없습니다: " + id));
    }

    public Page<Order> list(OrderStatus status, int page, int size) {
        List<Order> filtered = orders.findAll().stream()
                .filter(o -> status == null || o.status() == status)
                .toList();
        int fromIndex = Math.min((page - 1) * size, filtered.size());
        int toIndex = Math.min(fromIndex + size, filtered.size());
        return Page.of(filtered.subList(fromIndex, toIndex), page, size, filtered.size());
    }

    public Order fulfill(String id) {
        Order order = get(id);
        order.fulfill();
        orders.save(order);
        return order;
    }

    public Order markPaid(String id, String paymentId) {
        Order order = get(id);
        order.markPaid(paymentId);
        orders.save(order);
        return order;
    }
}
