package kr.elice.shop.cart.application;

import java.util.UUID;
import kr.elice.shop.cart.domain.Cart;
import kr.elice.shop.cart.domain.CartRepository;
import kr.elice.shop.catalog.application.CatalogService;
import kr.elice.shop.catalog.domain.Product;
import kr.elice.shop.catalog.domain.ProductStatus;
import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import org.springframework.stereotype.Service;

@Service
public class CartService {

    private final CartRepository carts;
    private final CatalogService catalog;

    public CartService(CartRepository carts, CatalogService catalog) {
        this.carts = carts;
        this.catalog = catalog;
    }

    public Cart create() {
        String id = "cart_" + UUID.randomUUID().toString().replace("-", "").substring(0, 8);
        Cart cart = Cart.create(id);
        carts.save(cart);
        return cart;
    }

    public Cart get(String id) {
        return carts.findById(id)
                .orElseThrow(() -> new DomainException(ErrorCode.NOT_FOUND, "장바구니를 찾을 수 없습니다: " + id));
    }

    public Cart addItem(String cartId, String productId, int quantity) {
        Product product = catalog.get(productId);
        if (product.status() == ProductStatus.ARCHIVED) {
            throw new DomainException(ErrorCode.PRODUCT_ARCHIVED, "아카이브된 상품은 담을 수 없습니다.");
        }
        Cart cart = get(cartId);
        cart.addItem(productId, quantity);
        carts.save(cart);
        return cart;
    }

    public Cart updateQuantity(String cartId, String productId, int quantity) {
        Cart cart = get(cartId);
        cart.updateQuantity(productId, quantity);
        carts.save(cart);
        return cart;
    }

    public Cart removeItem(String cartId, String productId) {
        Cart cart = get(cartId);
        cart.removeItem(productId);
        carts.save(cart);
        return cart;
    }

    public Cart clear(String cartId) {
        Cart cart = get(cartId);
        cart.clear();
        carts.save(cart);
        return cart;
    }
}
