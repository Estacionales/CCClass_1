package kr.elice.shop.catalog.web;

public record CreateProductRequest(String name, long price, int initialStock) {
}
