package kr.elice.shop.catalog.web;

import java.util.List;

public record ProductListResponse(List<ProductResponse> items, long total, int pages) {
}
