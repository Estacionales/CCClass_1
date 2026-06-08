package kr.elice.library.springboot;

import java.util.List;
import kr.elice.library.api.BookService;
import kr.elice.library.domain.Book;
import kr.elice.library.domain.LibraryException;
import kr.elice.library.store.BookStore;
import org.springframework.stereotype.Service;

/**
 * 신규 도서 모듈(Spring Boot)입니다. 레거시와 같은 BookService 계약을 만족하고,
 * 같은 공유 BookStore 를 사용해 전환 중에도 데이터 연속성을 지킵니다.
 *
 * <p>빈 이름이 newBookService 가 되어 module.books=new 일 때 라우터가 선택합니다.
 * 데모는 공유 인메모리 저장소를 쓰지만, 운영에서는 Spring Data JPA 리포지토리로
 * 저장소만 교체하면 됩니다. 지켜야 할 계약은 그대로입니다.</p>
 */
@Service
public class NewBookService implements BookService {

    private final BookStore store;

    public NewBookService(BookStore store) {
        this.store = store;
    }

    @Override
    public Book register(String title) {
        return store.save(new Book(store.nextId(), title));
    }

    @Override
    public Book get(String id) {
        return store.find(id).orElseThrow(() ->
                new LibraryException(LibraryException.Code.NOT_FOUND, "도서를 찾을 수 없습니다: " + id));
    }

    @Override
    public List<Book> list() {
        return store.all();
    }
}
