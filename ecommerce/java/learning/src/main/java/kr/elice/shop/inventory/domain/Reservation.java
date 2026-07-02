package kr.elice.shop.inventory.domain;

import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;

public class Reservation {

    private final String id;
    private final String productId;
    private final int quantity;
    private ReservationStatus status;

    private Reservation(String id, String productId, int quantity, ReservationStatus status) {
        this.id = id;
        this.productId = productId;
        this.quantity = quantity;
        this.status = status;
    }

    public static Reservation create(String id, String productId, int quantity) {
        return new Reservation(id, productId, quantity, ReservationStatus.RESERVED);
    }

    public void confirm() {
        requireReserved();
        this.status = ReservationStatus.CONFIRMED;
    }

    public void release() {
        requireReserved();
        this.status = ReservationStatus.RELEASED;
    }

    private void requireReserved() {
        if (status != ReservationStatus.RESERVED) {
            throw new DomainException(ErrorCode.INVALID_STATE_TRANSITION, "이미 처리된 예약입니다.");
        }
    }

    public String id() {
        return id;
    }

    public String productId() {
        return productId;
    }

    public int quantity() {
        return quantity;
    }

    public ReservationStatus status() {
        return status;
    }
}
