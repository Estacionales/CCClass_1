package kr.elice.shop.cart.domain;

import java.util.Optional;

public interface CartRepository {

    Cart save(Cart cart);

    Optional<Cart> findById(String id);
}
