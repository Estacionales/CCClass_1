package kr.elice.realfield.ingestion.client;

import java.util.List;

/**
 * 실거래 원천 추상화입니다. 운영은 data.go.kr 실호출(MolitApiClient), 실습·E2E는 오프라인
 * 결정적 스텁(StubAptTradeSource)을 프로필로 갈아끼웁니다. 수집 오케스트레이션은 이 계약에만
 * 의존하므로, 네트워크·인증키 없이도 부팅 E2E를 멱등하게 돌릴 수 있습니다.
 */
public interface AptTradeSource {
    List<MolitAptTradeItem> fetchAptTrades(String lawdCd, String dealYmd);
}
