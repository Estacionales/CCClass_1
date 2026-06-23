package kr.elice.realfield.config;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.config.server.EnableConfigServer;

/**
 * 설정 서버입니다. data.go.kr 인증키·엔드포인트·회복력 정책을 한곳에서 외부화해
 * 각 서비스가 기동 시 받아가게 합니다. 인증키는 코드·이미지에 박지 않습니다.
 */
@EnableConfigServer
@SpringBootApplication
public class ConfigServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(ConfigServerApplication.class, args);
    }
}
