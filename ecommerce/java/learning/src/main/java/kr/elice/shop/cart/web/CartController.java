package kr.elice.shop.cart.web;

import java.util.List;
import java.util.Map;
import kr.elice.shop.cart.application.CartService;
import kr.elice.shop.cart.domain.Cart;
import kr.elice.shop.catalog.application.CatalogService;
import kr.elice.shop.catalog.domain.Product;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/carts")
public class CartController {

    private final CartService cartService;
    private final CatalogService catalog;

    public CartController(CartService cartService, CatalogService catalog) {
        this.cartService = cartService;
        this.catalog = catalog;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public CreateCartResponse create() {
        Cart cart = cartService.create();
        return new CreateCartResponse(cart.id());
    }

    @GetMapping("/{id}")
    public CartView view(@PathVariable String id) {
        return buildView(cartService.get(id));
    }

    @PostMapping("/{id}/items")
    public CartView addItem(@PathVariable String id, @RequestBody AddItemRequest request) {
        Cart cart = cartService.addItem(id, request.productId(), request.qty());
        return buildView(cart);
    }

    @PatchMapping("/{id}/items/{productId}")
    public CartView updateItem(
            @PathVariable String id, @PathVariable String productId, @RequestBody UpdateItemRequest request) {
        Cart cart = cartService.updateQuantity(id, productId, request.qty());
        return buildView(cart);
    }

    @DeleteMapping("/{id}/items/{productId}")
    public CartView removeItem(@PathVariable String id, @PathVariable String productId) {
        Cart cart = cartService.removeItem(id, productId);
        return buildView(cart);
    }

    @PostMapping("/{id}/clear")
    public CartView clear(@PathVariable String id) {
        Cart cart = cartService.clear(id);
        return buildView(cart);
    }

    private CartView buildView(Cart cart) {
        List<CartLineView> lines = cart.items().entrySet().stream()
                .map(this::toLineView)
                .toList();
        long total = lines.stream().mapToLong(CartLineView::lineTotal).sum();
        return new CartView(cart.id(), lines, total);
    }

    private CartLineView toLineView(Map.Entry<String, Integer> entry) {
        Product product = catalog.get(entry.getKey());
        int qty = entry.getValue();
        long unitPrice = product.price().amount();
        return new CartLineView(product.id(), product.name(), unitPrice, qty, unitPrice * qty);
    }
}
