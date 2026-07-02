package kr.elice.shop.payment.domain;

import kr.elice.shop.shared.Money;

public interface PaymentGateway {

    boolean charge(String orderId, Money amount);
}
