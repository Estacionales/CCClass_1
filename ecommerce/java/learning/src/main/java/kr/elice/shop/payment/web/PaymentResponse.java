package kr.elice.shop.payment.web;

import kr.elice.shop.payment.domain.Payment;

public record PaymentResponse(String id, String orderId, long amount, String status) {

    public static PaymentResponse from(Payment payment) {
        return new PaymentResponse(
                payment.id(), payment.orderId(), payment.amount().amount(), payment.status().name());
    }
}
