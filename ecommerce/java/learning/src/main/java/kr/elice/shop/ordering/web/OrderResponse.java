package kr.elice.shop.ordering.web;

import kr.elice.shop.ordering.domain.Order;

public record OrderResponse(String id, String status, long totalAmount) {

    public static OrderResponse from(Order order) {
        return new OrderResponse(order.id(), order.status().name(), order.totalAmount().amount());
    }
}
