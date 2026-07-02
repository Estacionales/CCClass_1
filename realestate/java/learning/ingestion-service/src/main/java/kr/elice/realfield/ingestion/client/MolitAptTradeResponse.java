package kr.elice.realfield.ingestion.client;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

import java.util.List;

/**
 * MOLIT 상세 엔드포인트 XML 응답의 내부 DTO.
 * 형태 정본은 {@code 00_sources/01_apis/molit_apt_trade_api.md} §5.1(header + body.items.item[] + 페이징 메타).
 */
@JacksonXmlRootElement(localName = "response")
@JsonIgnoreProperties(ignoreUnknown = true)
public record MolitAptTradeResponse(
        @JsonProperty("header") Header header,
        @JsonProperty("body") Body body) {

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Header(
            @JsonProperty("resultCode") String resultCode,
            @JsonProperty("resultMsg") String resultMsg) {
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Body(
            @JsonProperty("items") Items items,
            @JsonProperty("numOfRows") Integer numOfRows,
            @JsonProperty("pageNo") Integer pageNo,
            @JsonProperty("totalCount") Integer totalCount) {
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Items(
            @JacksonXmlProperty(localName = "item")
            @JacksonXmlElementWrapper(useWrapping = false)
            @JsonProperty("item") List<MolitAptTradeItem> item) {
    }
}
