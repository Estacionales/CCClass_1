package kr.elice.library.platform;

import java.util.Map;
import kr.elice.library.domain.Loan;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 대출 요청(/loans)을 받는 앞단입니다. 라우터가 정한 활성 대출 구현으로 위임합니다.
 *
 * <p>대출 한도(AC-1)와 연체 거부(AC-2)는 활성 구현이 책임지므로, 컨트롤러는 규칙을
 * 알지 못한 채 위임만 합니다. 거부는 도메인 예외로 올라와 409 로 변환됩니다.</p>
 */
@RestController
@RequestMapping("/loans")
public class LoanController {

    private final LoanRouter router;

    public LoanController(LoanRouter router) {
        this.router = router;
    }

    public record BorrowRequest(String memberId, String bookId, Integer daysUntilDue) {}

    @PostMapping
    public ResponseEntity<LoanResponse> borrow(@RequestBody BorrowRequest req) {
        int days = req.daysUntilDue() == null ? 14 : req.daysUntilDue();
        Loan loan = router.loans().borrow(req.memberId(), req.bookId(), days);
        return ResponseEntity.status(HttpStatus.CREATED).body(LoanResponse.from(loan));
    }

    @PostMapping("/{id}/return")
    public Map<String, Object> giveBack(@PathVariable String id) {
        router.loans().giveBack(id);
        return Map.of("loanId", id, "returned", true);
    }

    @GetMapping("/member/{memberId}")
    public Map<String, Object> memberStatus(@PathVariable String memberId) {
        return Map.of(
                "memberId", memberId,
                "activeCount", router.loans().activeCount(memberId),
                "hasOverdue", router.loans().hasOverdue(memberId));
    }
}
