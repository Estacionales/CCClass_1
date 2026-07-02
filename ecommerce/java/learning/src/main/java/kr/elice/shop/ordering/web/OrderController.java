package kr.elice.shop.ordering.web;

import kr.elice.shop.ordering.application.OrderService;
import kr.elice.shop.ordering.domain.Order;
import kr.elice.shop.ordering.domain.OrderStatus;
import kr.elice.shop.shared.Page;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** 취소는 예약 해제·환불 보상을 조율해야 하므로 checkout.web.OrderCancelController 가 담당합니다. */
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @GetMapping
    public OrderListResponse list(
            @RequestParam(required = false) OrderStatus status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<Order> result = orderService.list(status, page, size);
        return new OrderListResponse(
                result.content().stream().map(OrderResponse::from).toList(),
                result.totalElements(),
                result.totalPages());
    }

    @GetMapping("/{id}")
    public OrderResponse get(@PathVariable String id) {
        return OrderResponse.from(orderService.get(id));
    }

    @PostMapping("/{id}/fulfill")
    public OrderResponse fulfill(@PathVariable String id) {
        return OrderResponse.from(orderService.fulfill(id));
    }
}
