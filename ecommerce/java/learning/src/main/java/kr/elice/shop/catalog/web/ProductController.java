package kr.elice.shop.catalog.web;

import kr.elice.shop.catalog.application.CatalogService;
import kr.elice.shop.catalog.domain.Product;
import kr.elice.shop.catalog.domain.ProductStatus;
import kr.elice.shop.shared.Page;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final CatalogService catalog;

    public ProductController(CatalogService catalog) {
        this.catalog = catalog;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ProductResponse create(
            @RequestBody CreateProductRequest request,
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey) {
        Product product = catalog.create(request.name(), request.price(), request.initialStock(), idempotencyKey);
        return ProductResponse.from(product);
    }

    @GetMapping
    public ProductListResponse list(
            @RequestParam(required = false) String q,
            @RequestParam(required = false) ProductStatus status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<Product> result = catalog.search(q, status, page, size);
        return new ProductListResponse(
                result.content().stream().map(ProductResponse::from).toList(),
                result.totalElements(),
                result.totalPages());
    }

    @GetMapping("/{id}")
    public ProductResponse get(@PathVariable String id) {
        return ProductResponse.from(catalog.get(id));
    }

    @PostMapping("/{id}/stock-additions")
    public ProductResponse addStock(@PathVariable String id, @RequestBody StockChangeRequest request) {
        return ProductResponse.from(catalog.addStock(id, request.quantity()));
    }

    @PostMapping("/{id}/stock-reductions")
    public ProductResponse reduceStock(@PathVariable String id, @RequestBody StockChangeRequest request) {
        return ProductResponse.from(catalog.reduceStock(id, request.quantity()));
    }

    @PostMapping("/{id}/archive")
    public ProductResponse archive(@PathVariable String id) {
        return ProductResponse.from(catalog.archive(id));
    }
}
