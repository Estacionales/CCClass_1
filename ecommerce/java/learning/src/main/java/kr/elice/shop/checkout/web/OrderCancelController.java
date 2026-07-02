package kr.elice.shop.checkout.web;

import kr.elice.shop.checkout.application.CheckoutService;
import kr.elice.shop.ordering.web.OrderResponse;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 주문 취소는 예약 해제와 결제 환불을 함께 조율해야 하므로 checkout 컨텍스트가 담당합니다.
 * 경로는 /api/orders/{id}/cancel 로 ordering 컨텍스트의 표면과 일치시킵니다.
 */
@RestController
@RequestMapping("/api/orders")
public class OrderCancelController {

    private final CheckoutService checkoutService;

    public OrderCancelController(CheckoutService checkoutService) {
        this.checkoutService = checkoutService;
    }

    @PostMapping("/{id}/cancel")
    public OrderResponse cancel(@PathVariable String id) {
        return OrderResponse.from(checkoutService.cancelOrder(id));
    }
}
