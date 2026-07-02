package kr.elice.shop.inventory.web;

import kr.elice.shop.inventory.application.InventoryService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/inventory")
public class InventoryController {

    private final InventoryService inventory;

    public InventoryController(InventoryService inventory) {
        this.inventory = inventory;
    }

    @GetMapping("/{productId}")
    public AvailabilityResponse available(@PathVariable String productId) {
        return new AvailabilityResponse(productId, inventory.available(productId));
    }
}
