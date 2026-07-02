package kr.elice.shop.ordering.domain;

import kr.elice.shop.shared.Money;

public class OrderLine {

    private final String productId;
    private final String productName;
    private final Money unitPrice;
    private final int quantity;

    public OrderLine(String productId, String productName, Money unitPrice, int quantity) {
        this.productId = productId;
        this.productName = productName;
        this.unitPrice = unitPrice;
        this.quantity = quantity;
    }

    public Money lineTotal() {
        return unitPrice.times(quantity);
    }

    public String productId() {
        return productId;
    }

    public String productName() {
        return productName;
    }

    public Money unitPrice() {
        return unitPrice;
    }

    public int quantity() {
        return quantity;
    }
}
