package kr.elice.library.platform;

import java.util.Map;
import kr.elice.library.domain.LibraryException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * 도메인 예외를 일관된 JSON 오류 응답으로 변환합니다.
 *
 * <p>대출 한도 초과·연체는 409, 미존재는 404 로 매핑합니다. 라우터가 아직 만들어지지
 * 않은 신규 구현을 가리킬 때 나는 상태 오류는 409 로 돌려주어, 무엇을 구현해야 하는지
 * 메시지로 안내합니다.</p>
 */
@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler(LibraryException.class)
    public ResponseEntity<Map<String, String>> handle(LibraryException ex) {
        HttpStatus status = switch (ex.code()) {
            case NOT_FOUND -> HttpStatus.NOT_FOUND;
            case LOAN_LIMIT_EXCEEDED, OVERDUE_EXISTS -> HttpStatus.CONFLICT;
        };
        return ResponseEntity.status(status)
                .body(Map.of("code", ex.code().name(), "message", ex.getMessage()));
    }

    @ExceptionHandler(IllegalStateException.class)
    public ResponseEntity<Map<String, String>> handleState(IllegalStateException ex) {
        return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(Map.of("code", "MIGRATION_INCOMPLETE", "message", ex.getMessage()));
    }
}
