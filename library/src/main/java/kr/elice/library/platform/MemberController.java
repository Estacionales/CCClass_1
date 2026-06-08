package kr.elice.library.platform;

import kr.elice.library.domain.Member;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 회원 요청(/members)을 받는 앞단입니다. 라우터가 정한 활성 구현으로 위임합니다.
 */
@RestController
@RequestMapping("/members")
public class MemberController {

    private final CatalogRouter router;

    public MemberController(CatalogRouter router) {
        this.router = router;
    }

    public record CreateRequest(String name) {}

    @PostMapping
    public ResponseEntity<Member> register(@RequestBody CreateRequest req) {
        return ResponseEntity.status(HttpStatus.CREATED).body(router.members().register(req.name()));
    }

    @GetMapping("/{id}")
    public Member get(@PathVariable String id) {
        return router.members().get(id);
    }
}
