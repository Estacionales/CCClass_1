package kr.elice.realfield.ingestion;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.loadbalancer.LoadBalanced;
import org.springframework.context.annotation.Bean;
import org.springframework.web.reactive.function.client.WebClient;

/** 수집 서비스입니다. data.go.kr 실거래가 API를 호출해 표준 스키마로 정규화하고 거래원장으로 넘깁니다. */
@SpringBootApplication
public class IngestionApplication {
    public static void main(String[] args) {
        SpringApplication.run(IngestionApplication.class, args);
    }

    /** 디스커버리 기반 로드밸런싱 WebClient. lb://transaction-service 로 거래원장에 적재 요청합니다. */
    @Bean
    @LoadBalanced
    WebClient.Builder loadBalancedWebClientBuilder() {
        return WebClient.builder();
    }
}
