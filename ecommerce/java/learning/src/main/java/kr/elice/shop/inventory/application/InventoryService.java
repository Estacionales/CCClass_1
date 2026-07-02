package kr.elice.shop.inventory.application;

import java.util.UUID;
import kr.elice.shop.catalog.application.CatalogService;
import kr.elice.shop.catalog.domain.Product;
import kr.elice.shop.inventory.domain.Reservation;
import kr.elice.shop.inventory.domain.ReservationRepository;
import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;

public class InventoryService {

    private final CatalogService catalog;
    private final ReservationRepository reservations;

    public InventoryService(CatalogService catalog, ReservationRepository reservations) {
        this.catalog = catalog;
        this.reservations = reservations;
    }

    public synchronized Reservation reserve(String productId, int quantity) {
        int available = available(productId);
        if (quantity > available) {
            throw new DomainException(ErrorCode.INSUFFICIENT_STOCK, "예약 가능한 재고가 부족합니다.");
        }
        String id = "resv_" + UUID.randomUUID().toString().replace("-", "").substring(0, 8);
        Reservation reservation = Reservation.create(id, productId, quantity);
        reservations.save(reservation);
        return reservation;
    }

    public void confirm(String reservationId) {
        Reservation reservation = get(reservationId);
        reservation.confirm();
        catalog.reduceStock(reservation.productId(), reservation.quantity());
        reservations.save(reservation);
    }

    public void release(String reservationId) {
        Reservation reservation = get(reservationId);
        reservation.release();
        reservations.save(reservation);
    }

    public int available(String productId) {
        Product product = catalog.get(productId);
        int reserved = reservations.findActiveByProductId(productId).stream()
                .mapToInt(Reservation::quantity)
                .sum();
        return product.stockQuantity() - reserved;
    }

    private Reservation get(String id) {
        return reservations.findById(id)
                .orElseThrow(() -> new DomainException(ErrorCode.NOT_FOUND, "예약을 찾을 수 없습니다: " + id));
    }
}
