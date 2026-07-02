package kr.elice.shop.catalog.application;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import kr.elice.shop.catalog.domain.Product;
import kr.elice.shop.catalog.domain.ProductRepository;
import kr.elice.shop.catalog.domain.ProductStatus;
import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import kr.elice.shop.shared.Money;
import kr.elice.shop.shared.Page;

public class CatalogService {

    private final ProductRepository products;
    private final Map<String, String> idempotencyKeys = new ConcurrentHashMap<>();

    public CatalogService(ProductRepository products) {
        this.products = products;
    }

    public Product create(String name, long price, int stockQuantity, String idempotencyKey) {
        if (idempotencyKey != null) {
            String existingId = idempotencyKeys.get(idempotencyKey);
            if (existingId != null) {
                return get(existingId);
            }
        }
        String id = "prod_" + UUID.randomUUID().toString().replace("-", "").substring(0, 8);
        Product product = Product.create(id, name, Money.won(price), stockQuantity);
        products.save(product);
        if (idempotencyKey != null) {
            idempotencyKeys.put(idempotencyKey, id);
        }
        return product;
    }

    public Product get(String id) {
        return products.findById(id)
                .orElseThrow(() -> new DomainException(ErrorCode.NOT_FOUND, "상품을 찾을 수 없습니다: " + id));
    }

    public Page<Product> search(String name, ProductStatus status, int page, int size) {
        List<Product> filtered = products.findAll().stream()
                .filter(p -> name == null || p.name().contains(name))
                .filter(p -> status == null || p.status() == status)
                .toList();
        int fromIndex = Math.min(page * size, filtered.size());
        int toIndex = Math.min(fromIndex + size, filtered.size());
        return Page.of(filtered.subList(fromIndex, toIndex), page, size, filtered.size());
    }

    public Product addStock(String id, int quantity) {
        Product product = get(id);
        product.addStock(quantity);
        products.save(product);
        return product;
    }

    public Product reduceStock(String id, int quantity) {
        Product product = get(id);
        product.reduceStock(quantity);
        products.save(product);
        return product;
    }

    public Product archive(String id) {
        Product product = get(id);
        product.archive();
        products.save(product);
        return product;
    }
}
