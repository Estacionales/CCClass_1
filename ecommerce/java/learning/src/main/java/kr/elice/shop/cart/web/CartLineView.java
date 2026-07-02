package kr.elice.shop.cart.web;

public record CartLineView(String productId, String name, long unitPrice, int qty, long lineTotal) {
}
