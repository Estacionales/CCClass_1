package kr.elice.realfield.ingestion.client;

import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

/**
 * MOLIT(data.go.kr) 아파트 매매 실거래 상세 엔드포인트 호출 경계.
 *
 * <p>단일 페이지를 조회한다(전량 페이징 루프는 본 턴 범위 밖). 외부 장애는 resilience4j
 * {@code @Retry}·{@code @CircuitBreaker}(인스턴스명 {@code molitApi}, 정책값은 config-server의
 * {@code resilience4j.*}와 동일)로 수집 경계 안에 가둔다(AC-2, {@code 07_integration} §4).
 *
 * <p>보안(SEC-003): serviceKey 및 키를 포함한 전체 URL을 로그·예외 메시지에 남기지 않는다.
 * 로그에는 path·질의 파라미터만 남기고 serviceKey는 {@code ***}로 마스킹한다.
 */
@Component
public class MolitApiClient {

    private static final Logger log = LoggerFactory.getLogger(MolitApiClient.class);

    private final WebClient webClient;
    private final String aptTradePath;
    private final String serviceKey;

    public MolitApiClient(
            WebClient.Builder webClientBuilder,
            @Value("${molit.base-url}") String baseUrl,
            @Value("${molit.apt-trade-path}") String aptTradePath,
            @Value("${molit.service-key:}") String serviceKey) {
        this.webClient = webClientBuilder.baseUrl(baseUrl).build();
        this.aptTradePath = aptTradePath;
        this.serviceKey = serviceKey;
    }

    /**
     * 한 페이지({@code pageNo})를 조회해 XML 응답을 파싱한다.
     * 서블릿 스택이므로 {@code block()} 허용(build.gradle 주석).
     */
    @Retry(name = "molitApi")
    @CircuitBreaker(name = "molitApi", fallbackMethod = "fetchPageFallback")
    public MolitFetchResult fetchPage(String sggCd, String dealYmd, int pageNo, int numOfRows) {
        log.info("MOLIT 호출 path={} LAWD_CD={} DEAL_YMD={} pageNo={} numOfRows={} serviceKey=***",
                aptTradePath, sggCd, dealYmd, pageNo, numOfRows);

        MolitAptTradeResponse response = webClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path(aptTradePath)
                        .queryParam("serviceKey", serviceKey)
                        .queryParam("LAWD_CD", sggCd)
                        .queryParam("DEAL_YMD", dealYmd)
                        .queryParam("pageNo", pageNo)
                        .queryParam("numOfRows", numOfRows)
                        .build())
                .retrieve()
                .bodyToMono(MolitAptTradeResponse.class)
                .block();

        return MolitFetchResult.ok(response);
    }

    /**
     * resilience4j fallback: 재시도 소진·서킷 오픈 시 진입한다.
     * raw 예외를 밖으로 던지지 않고 null도 반환하지 않는다 — 실패 결과 객체로 감싼다.
     * serviceKey·전체 URL이 유출되지 않도록 예외 메시지 대신 예외 클래스명만 기록한다(SEC-003).
     */
    @SuppressWarnings("unused")
    private MolitFetchResult fetchPageFallback(String sggCd, String dealYmd, int pageNo, int numOfRows, Throwable t) {
        String reason = t.getClass().getSimpleName();
        log.warn("MOLIT 호출 실패(재시도 소진 또는 서킷 오픈) LAWD_CD={} DEAL_YMD={} pageNo={} cause={}",
                sggCd, dealYmd, pageNo, reason);
        return MolitFetchResult.failed(reason);
    }
}
