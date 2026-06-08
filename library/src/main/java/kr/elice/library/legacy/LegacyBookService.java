package kr.elice.library.legacy;

import java.util.List;
import kr.elice.library.api.BookService;
import kr.elice.library.domain.Book;
import kr.elice.library.domain.LibraryException;
import kr.elice.library.store.BookStore;
import org.springframework.stereotype.Service;

/**
 * 레거시 도서 모듈입니다. 구식 모놀리식 스타일의 시작 코드이며, 학습자는 이 코드를
 * 스펙으로 풀어 springboot 패키지에 새로 구현합니다.
 *
 * <p>저장소는 공유 BookStore 를 사용합니다. 전환 중 신규 구현과 같은 데이터를 보므로,
 * 도서 모듈을 신규로 전환해도 아직 레거시인 대출 모듈이 같은 도서를 그대로 찾습니다.</p>
 */
@Service
public class LegacyBookService implements BookService {

    private final BookStore store;

    public LegacyBookService(BookStore store) {
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
