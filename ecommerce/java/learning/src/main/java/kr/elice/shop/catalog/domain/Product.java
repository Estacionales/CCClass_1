package kr.elice.shop.catalog.domain;

import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import kr.elice.shop.shared.Money;

public class Product {

    private final String id;
    private final String name;
    private final Money price;
    private int stockQuantity;
    private ProductStatus status;

    private Product(String id, String name, Money price, int stockQuantity, ProductStatus status) {
        this.id = id;
        this.name = name;
        this.price = price;
        this.stockQuantity = stockQuantity;
        this.status = status;
    }

    public static Product create(String id, String name, Money price, int stockQuantity) {
        if (!price.isPositive()) {
            throw new DomainException(ErrorCode.INVALID_PRICE, "가격은 0원보다 커야 합니다.");
        }
        return new Product(id, name, price, stockQuantity, ProductStatus.ACTIVE);
    }

    public void addStock(int quantity) {
        requireActive();
        this.stockQuantity += quantity;
    }

    public void reduceStock(int quantity) {
        requireActive();
        if (quantity > stockQuantity) {
            throw new DomainException(ErrorCode.INSUFFICIENT_STOCK, "재고가 부족합니다.");
        }
        this.stockQuantity -= quantity;
    }

    public void archive() {
        this.status = ProductStatus.ARCHIVED;
    }

    private void requireActive() {
        if (status != ProductStatus.ACTIVE) {
            throw new DomainException(ErrorCode.PRODUCT_ARCHIVED, "아카이브된 상품은 재고를 변경할 수 없습니다.");
        }
    }

    public String id() {
        return id;
    }

    public String name() {
        return name;
    }

    public Money price() {
        return price;
    }

    public int stockQuantity() {
        return stockQuantity;
    }

    public ProductStatus status() {
        return status;
    }
}
