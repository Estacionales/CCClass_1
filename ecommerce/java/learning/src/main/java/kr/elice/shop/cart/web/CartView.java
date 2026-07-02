package kr.elice.shop.cart.web;

import java.util.List;

public record CartView(String cartId, List<CartLineView> items, long totalAmount) {
}
