package kr.elice.shop.cart.domain;

import java.util.LinkedHashMap;
import java.util.Map;

public class Cart {

    private final String id;
    private final Map<String, Integer> items = new LinkedHashMap<>();

    private Cart(String id) {
        this.id = id;
    }

    public static Cart create(String id) {
        return new Cart(id);
    }

    public void addItem(String productId, int quantity) {
        items.merge(productId, quantity, Integer::sum);
    }

    public void updateQuantity(String productId, int quantity) {
        if (quantity <= 0) {
            items.remove(productId);
            return;
        }
        items.put(productId, quantity);
    }

    public void removeItem(String productId) {
        items.remove(productId);
    }

    public void clear() {
        items.clear();
    }

    public String id() {
        return id;
    }

    public Map<String, Integer> items() {
        return Map.copyOf(items);
    }
}
