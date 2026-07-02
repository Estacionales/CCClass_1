package kr.elice.realfield.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/** 단일 진입점(API Gateway)입니다. 외부 요청을 디스커버리로 찾은 도메인 서비스로 라우팅합니다. */
@SpringBootApplication
public class ApiGatewayApplication {
    public static void main(String[] args) {
        SpringApplication.run(ApiGatewayApplication.class, args);
    }
}
