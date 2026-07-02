package kr.elice.library.springboot;

import java.util.List;
import kr.elice.library.api.BookService;
import kr.elice.library.domain.Book;
import kr.elice.library.domain.LibraryException;
import kr.elice.library.store.BookStore;
import org.springframework.stereotype.Service;

/**
 * 도서 모듈의 신규 구현입니다. 레거시 {@code LegacyBookService} 를 대체하며,
 * 라우터는 이 빈을 기본 이름 {@code newBookService} 로 찾아 사용합니다.
 *
 * <p>저장소는 레거시와 같은 공유 {@link BookStore} 를 사용하므로, 도서 모듈만
 * 신규로 전환해도 아직 레거시인 대출 모듈이 같은 도서 데이터를 그대로 찾습니다.</p>
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
