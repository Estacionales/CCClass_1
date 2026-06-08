package kr.elice.library.api;

import java.util.List;
import kr.elice.library.domain.Book;

/**
 * 도서 모듈 계약입니다. legacy 와 springboot 두 구현이 이 인터페이스를 똑같이 만족합니다.
 * 라우터는 이 인터페이스 타입으로 활성 구현을 선택합니다.
 */
public interface BookService {

    Book register(String title);

    Book get(String id);

    List<Book> list();
}
