package kr.elice.shop.inventory.domain;

import java.util.List;
import java.util.Optional;

public interface ReservationRepository {

    Reservation save(Reservation reservation);

    Optional<Reservation> findById(String id);

    List<Reservation> findActiveByProductId(String productId);
}
