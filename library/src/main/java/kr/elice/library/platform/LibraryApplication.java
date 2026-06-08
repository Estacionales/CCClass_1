package kr.elice.library.platform;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.PropertySource;

/**
 * 도서관 애플리케이션 진입점입니다.
 *
 * <p>kr.elice.library 전체를 컴포넌트 스캔합니다. legacy 패키지의 구현은 항상 존재하고,
 * springboot 패키지의 신규 구현은 학습자가 추가하면 자동으로 빈으로 등록됩니다.
 * 어떤 구현을 쓸지는 migration.properties 가 모듈 단위로 결정합니다.</p>
 */
@SpringBootApplication(scanBasePackages = "kr.elice.library")
@PropertySource("classpath:migration.properties")
public class LibraryApplication {

    public static void main(String[] args) {
        SpringApplication.run(LibraryApplication.class, args);
    }
}
