package kr.elice.library.store;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import kr.elice.library.domain.Book;
import org.springframework.stereotype.Component;

/**
 * 도서 공유 저장소입니다. 전환 중 레거시 구현과 신규 구현이 같은 데이터를 봅니다.
 *
 * <p>실제 strangler 전환에서는 두 구현이 같은 데이터베이스를 공유합니다. 이 데모는
 * 그 공유 데이터베이스를 인메모리 저장소 빈 하나로 표현합니다. 그래서 도서 모듈을
 * 신규로 전환해도, 아직 레거시인 대출 모듈이 같은 도서 데이터를 그대로 찾습니다.</p>
 */
@Component
public class BookStore {

    private final Map<String, Book> rows = new ConcurrentHashMap<>();
    private final AtomicLong seq = new AtomicLong(0);

    public String nextId() {
        return "book_" + seq.incrementAndGet();
    }

    public Book save(Book book) {
        rows.put(book.id(), book);
        return book;
    }

    public Optional<Book> find(String id) {
        return Optional.ofNullable(rows.get(id));
    }

    public List<Book> all() {
        return new ArrayList<>(rows.values());
    }
}
