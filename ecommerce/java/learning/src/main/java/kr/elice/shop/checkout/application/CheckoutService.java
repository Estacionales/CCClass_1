package kr.elice.shop.checkout.application;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import kr.elice.shop.cart.domain.Cart;
import kr.elice.shop.cart.domain.CartRepository;
import kr.elice.shop.catalog.application.CatalogService;
import kr.elice.shop.catalog.domain.Product;
import kr.elice.shop.inventory.application.InventoryService;
import kr.elice.shop.inventory.domain.Reservation;
import kr.elice.shop.ordering.domain.Order;
import kr.elice.shop.ordering.domain.OrderLine;
import kr.elice.shop.ordering.domain.OrderRepository;
import kr.elice.shop.payment.application.PaymentService;
import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import org.springframework.stereotype.Service;

@Service
public class CheckoutService {

    private final CartRepository carts;
    private final CatalogService catalog;
    private final InventoryService inventory;
    private final OrderRepository orders;
    private final PaymentService payments;
    private final Map<String, String> idempotencyKeys = new ConcurrentHashMap<>();

    public CheckoutService(
            CartRepository carts,
            CatalogService catalog,
            InventoryService inventory,
            OrderRepository orders,
            PaymentService payments) {
        this.carts = carts;
        this.catalog = catalog;
        this.inventory = inventory;
        this.orders = orders;
        this.payments = payments;
    }

    public Order checkout(String cartId, String idempotencyKey) {
        if (idempotencyKey != null) {
            String existingId = idempotencyKeys.get(idempotencyKey);
            if (existingId != null) {
                return findOrder(existingId);
            }
        }

        Cart cart = carts.findById(cartId)
                .orElseThrow(() -> new DomainException(ErrorCode.NOT_FOUND, "장바구니를 찾을 수 없습니다: " + cartId));

        List<String> reservationIds = new ArrayList<>();
        List<OrderLine> lines = new ArrayList<>();
        try {
            for (Map.Entry<String, Integer> item : cart.items().entrySet()) {
                String productId = item.getKey();
                int quantity = item.getValue();
                Reservation reservation = inventory.reserve(productId, quantity);
                reservationIds.add(reservation.id());
                Product product = catalog.get(productId);
                lines.add(new OrderLine(productId, product.name(), product.price(), quantity));
            }
        } catch (DomainException ex) {
            for (String reservationId : reservationIds) {
                inventory.release(reservationId);
            }
            throw ex;
        }

        String orderId = "ord_" + UUID.randomUUID().toString().replace("-", "").substring(0, 8);
        Order order = Order.create(orderId, lines, reservationIds);
        orders.save(order);
        if (idempotencyKey != null) {
            idempotencyKeys.put(idempotencyKey, orderId);
        }
        return order;
    }

    public Order cancelOrder(String orderId) {
        Order order = findOrder(orderId);
        boolean requiresRefund = order.cancel();
        orders.save(order);
        for (String reservationId : order.reservationIds()) {
            inventory.compensate(reservationId);
        }
        if (requiresRefund) {
            payments.refundByOrderId(orderId);
        }
        return order;
    }

    private Order findOrder(String orderId) {
        return orders.findById(orderId)
                .orElseThrow(() -> new DomainException(ErrorCode.NOT_FOUND, "주문을 찾을 수 없습니다: " + orderId));
    }
}
