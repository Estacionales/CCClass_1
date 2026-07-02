package kr.elice.shop.shared;

import org.springframework.http.HttpStatus;

public enum ErrorCode {
    INVALID_PRICE(HttpStatus.BAD_REQUEST),
    INVALID_AMOUNT(HttpStatus.BAD_REQUEST),
    INSUFFICIENT_STOCK(HttpStatus.CONFLICT),
    PRODUCT_ARCHIVED(HttpStatus.CONFLICT),
    PAYMENT_REQUIRED(HttpStatus.CONFLICT),
    INVALID_STATE_TRANSITION(HttpStatus.CONFLICT),
    PAYMENT_DECLINED(HttpStatus.PAYMENT_REQUIRED),
    REFUND_NOT_ALLOWED(HttpStatus.CONFLICT),
    NOT_FOUND(HttpStatus.NOT_FOUND);

    private final HttpStatus httpStatus;

    ErrorCode(HttpStatus httpStatus) {
        this.httpStatus = httpStatus;
    }

    public HttpStatus httpStatus() {
        return httpStatus;
    }
}
