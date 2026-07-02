package kr.elice.shop.ordering.web;

import java.util.List;

public record OrderListResponse(List<OrderResponse> items, long total, int pages) {
}
