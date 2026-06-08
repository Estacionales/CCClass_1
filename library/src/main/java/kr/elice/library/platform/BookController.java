package kr.elice.library.platform;

import java.util.List;
import kr.elice.library.domain.Book;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 도서 요청(/books)을 받는 앞단입니다. 라우터가 정한 활성 구현(legacy 또는 new)으로
 * 그대로 위임합니다. 컨트롤러는 어느 구현이 처리하는지 알지 못합니다.
 */
@RestController
@RequestMapping("/books")
public class BookController {

    private final CatalogRouter router;

    public BookController(CatalogRouter router) {
        this.router = router;
    }

    public record CreateRequest(String title) {}

    @PostMapping
    public ResponseEntity<Book> register(@RequestBody CreateRequest req) {
        return ResponseEntity.status(HttpStatus.CREATED).body(router.books().register(req.title()));
    }

    @GetMapping("/{id}")
    public Book get(@PathVariable String id) {
        return router.books().get(id);
    }

    @GetMapping
    public List<Book> list() {
        return router.books().list();
    }
}
