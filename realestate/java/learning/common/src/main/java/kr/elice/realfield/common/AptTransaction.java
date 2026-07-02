package kr.elice.realfield.common;

/**
 * 정규화된 아파트 매매 실거래 1건의 표준 표현(공유 계약).
 *
 * <p>필드 구성은 이 저장소에 이미 커밋되어 있던 {@code transaction-service}(IdempotentUpsertTest)·
 * {@code analytics-service}(MarketStatCalculatorTest)의 고정 테스트가 pin한 11개 필드·순서를 그대로
 * 따른다. {@code 01_planning/04_data/realprice_data.md} §1.1의 전체 필드 표(umdCd·aptSeq·aptDong·
 * rgstDate·slerGbn·buyerGbn·estateAgentSggNm·landLeaseholdGbn·canceledDate 등)는 이 최소 계약보다
 * 넓다 — 그 차이는 알려진 드리프트이며 `sdd/03_build/01_feature/02_t1_ingestion.md`에 기록한다.
 *
 * <p>이 타입은 {@code AptTransactionNormalizer}의 출력이며, T2의 batch-upsert 계약이 받는 입력 타입이다.
 */
public record AptTransaction(
        String sggCd,
        String umdNm,
        String aptNm,
        double exclusiveArea,
        int floor,
        Integer buildYear,
        int dealYear,
        int dealMonth,
        int dealDay,
        long dealAmountWon,
        boolean canceled) {

    /**
     * 자연키(DAR-003, {@code 04_data} §1.2): 데이터 품질 게이트가 상시 보장하는 필수 항목만으로 구성한다.
     * {@code buildYear}·{@code canceled}는 재수집 시 값이 바뀔 수 있는 항목이라 키에서 제외한다
     * (해제 상태 전환이 같은 거래를 다른 키로 만들면 안 된다, CONR-005).
     */
    public String naturalKey() {
        return String.join("|",
                sggCd, umdNm, aptNm,
                String.valueOf(exclusiveArea),
                String.valueOf(floor),
                String.valueOf(dealYear),
                String.valueOf(dealMonth),
                String.valueOf(dealDay),
                String.valueOf(dealAmountWon));
    }
}
