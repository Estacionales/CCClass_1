package kr.elice.realfield.ingestion.client;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * MOLIT 상세 엔드포인트 응답의 원천 거래 item(파싱 직후, 정규화 전).
 *
 * <p>원천 타입은 전량 XML 문자열이다(CONR-002). 형 변환·정합은 {@code AptTransactionNormalizer}가
 * {@code common} 계약에 위임해 수행한다. 채택하지 않은 주소 부속 코드(landCd/bonbun/roadNm* 등)는
 * {@code @JsonIgnoreProperties(ignoreUnknown = true)}로 무시한다({@code 04_data} §1.1 미채택 항목).
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record MolitAptTradeItem(
        @JsonProperty("sggCd") String sggCd,
        @JsonProperty("umdNm") String umdNm,
        @JsonProperty("jibun") String jibun,
        @JsonProperty("aptNm") String aptNm,
        @JsonProperty("excluUseAr") String excluUseAr,
        @JsonProperty("dealYear") String dealYear,
        @JsonProperty("dealMonth") String dealMonth,
        @JsonProperty("dealDay") String dealDay,
        @JsonProperty("dealAmount") String dealAmount,
        @JsonProperty("floor") String floor,
        @JsonProperty("buildYear") String buildYear,
        @JsonProperty("dealingGbn") String dealingGbn,
        @JsonProperty("cdealType") String cdealType,
        @JsonProperty("cdealDay") String cdealDay) {
}
