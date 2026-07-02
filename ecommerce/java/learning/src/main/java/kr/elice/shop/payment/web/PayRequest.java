package kr.elice.shop.payment.web;

public record PayRequest(String orderId, String method) {
}
