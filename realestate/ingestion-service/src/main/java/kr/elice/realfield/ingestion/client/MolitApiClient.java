package kr.elice.realfield.ingestion.client;

import com.fasterxml.jackson.dataformat.xml.XmlMapper;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

/**
 * data.go.kr 국토교통부 아파트 매매 실거래가 OpenAPI 클라이언트입니다.
 *
 * <p>요구사항 AC-2(회복력)를 코드 계약으로 내립니다. 호출에 재시도 3회와 서킷브레이커를 적용하고,
 * 모두 실패하면 빈 결과로 우아하게 저하합니다. 외부 API가 죽어도 수집 파이프라인 전체가 멈추지 않습니다.
 */
@Component
@Profile("!stub")
public class MolitApiClient implements AptTradeSource {

    private final WebClient webClient;
    private final XmlMapper xmlMapper = new XmlMapper();
    private final String aptTradePath;
    private final String serviceKey;
    private final int numOfRows;

    public MolitApiClient(WebClient.Builder builder,
                          @Value("${molit.base-url}") String baseUrl,
                          @Value("${molit.apt-trade-path}") String aptTradePath,
                          @Value("${molit.service-key:}") String serviceKey,
                          @Value("${molit.num-of-rows:1000}") int numOfRows) {
        this.webClient = builder.baseUrl(baseUrl).build();
        this.aptTradePath = aptTradePath;
        this.serviceKey = serviceKey;
        this.numOfRows = numOfRows;
    }

    /**
     * 특정 시군구(lawdCd)·계약월(dealYmd)의 매매 실거래를 조회합니다.
     *
     * @param lawdCd  법정동코드 5자리 (예: 서울 종로구 11110)
     * @param dealYmd 계약월 YYYYMM (예: 202405)
     */
    @Override
    @Retry(name = "molitApi")
    @CircuitBreaker(name = "molitApi", fallbackMethod = "fallback")
    public List<MolitAptTradeItem> fetchAptTrades(String lawdCd, String dealYmd) {
        String xml = webClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path(aptTradePath)
                        .queryParam("serviceKey", serviceKey)
                        .queryParam("LAWD_CD", lawdCd)
                        .queryParam("DEAL_YMD", dealYmd)
                        .queryParam("pageNo", 1)
                        .queryParam("numOfRows", numOfRows)
                        .build())
                .retrieve()
                .bodyToMono(String.class)
                .block();
        return parseItems(xml);
    }

    /** AC-2: 재시도·서킷브레이커가 모두 실패하면 빈 결과로 저하합니다(부분 수집 허용). */
    @SuppressWarnings("unused")
    private List<MolitAptTradeItem> fallback(String lawdCd, String dealYmd, Throwable t) {
        return List.of();
    }

    private List<MolitAptTradeItem> parseItems(String xml) {
        if (xml == null || xml.isBlank()) return List.of();
        try {
            MolitResponse response = xmlMapper.readValue(xml, MolitResponse.class);
            return response.items();
        } catch (Exception e) {
            throw new IllegalStateException("data.go.kr 응답 파싱 실패", e);
        }
    }
}
