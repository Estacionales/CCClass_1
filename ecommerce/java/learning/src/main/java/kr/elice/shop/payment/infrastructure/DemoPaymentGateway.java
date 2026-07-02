package kr.elice.shop.payment.infrastructure;

import kr.elice.shop.payment.domain.PaymentGateway;
import kr.elice.shop.shared.Money;
import org.springframework.stereotype.Component;

/** 결정적으로 동작하는 데모 게이트웨이입니다. method 가 "declined" 이면 거절합니다. */
@Component
public class DemoPaymentGateway implements PaymentGateway {

    @Override
    public boolean charge(String orderId, Money amount, String method) {
        return method == null || !method.equalsIgnoreCase("declined");
    }
}
