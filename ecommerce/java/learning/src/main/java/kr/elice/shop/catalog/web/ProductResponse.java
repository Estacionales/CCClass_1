package kr.elice.shop.catalog.web;

import kr.elice.shop.catalog.domain.Product;

public record ProductResponse(String id, String name, long price, int stockQuantity, String status) {

    public static ProductResponse from(Product product) {
        return new ProductResponse(
                product.id(), product.name(), product.price().amount(), product.stockQuantity(),
                product.status().name());
    }
}
