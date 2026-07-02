package kr.elice.shop.payment.web;

import kr.elice.shop.payment.application.PaymentService;
import kr.elice.shop.payment.domain.Payment;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/payments")
public class PaymentController {

    private final PaymentService paymentService;

    public PaymentController(PaymentService paymentService) {
        this.paymentService = paymentService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public PaymentResponse pay(
            @RequestBody PayRequest request,
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey) {
        Payment payment = paymentService.pay(request.orderId(), request.method(), idempotencyKey);
        return PaymentResponse.from(payment);
    }

    @GetMapping("/{id}")
    public PaymentResponse get(@PathVariable String id) {
        return PaymentResponse.from(paymentService.get(id));
    }

    @PostMapping("/{id}/refund")
    public PaymentResponse refund(@PathVariable String id) {
        return PaymentResponse.from(paymentService.refund(id));
    }
}
