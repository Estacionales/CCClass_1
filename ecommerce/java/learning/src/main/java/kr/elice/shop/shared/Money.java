package kr.elice.shop.shared;

import java.util.Objects;

public final class Money {

    private final long amount;

    private Money(long amount) {
        if (amount < 0) {
            throw new DomainException(ErrorCode.INVALID_PRICE, "금액은 음수일 수 없습니다.");
        }
        this.amount = amount;
    }

    public static Money won(long amount) {
        return new Money(amount);
    }

    public long amount() {
        return amount;
    }

    public boolean isPositive() {
        return amount > 0;
    }

    public Money plus(Money other) {
        return new Money(this.amount + other.amount);
    }

    public Money times(int quantity) {
        return new Money(this.amount * quantity);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof Money other)) {
            return false;
        }
        return amount == other.amount;
    }

    @Override
    public int hashCode() {
        return Objects.hash(amount);
    }

    @Override
    public String toString() {
        return String.valueOf(amount);
    }
}
