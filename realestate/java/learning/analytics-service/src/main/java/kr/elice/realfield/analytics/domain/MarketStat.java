package kr.elice.realfield.analytics.domain;

/**
 * 시세 통계 read model입니다. 거래원장을 그대로 노출하지 않고, 조회에 최적화된 집계만 돌려줍니다.
 *
 * @param sggCd               시군구코드
 * @param dealYear            계약년
 * @param dealMonth           계약월
 * @param tradeCount          집계 대상 거래 수 (해제거래 제외)
 * @param medianPriceWon      중위 거래금액(원)
 * @param medianPricePerM2Won 중위 ㎡당 단가(원)
 */
public record MarketStat(
        String sggCd,
        int dealYear,
        int dealMonth,
        int tradeCount,
        long medianPriceWon,
        long medianPricePerM2Won
) {
    public static MarketStat empty(String sggCd, int dealYear, int dealMonth) {
        return new MarketStat(sggCd, dealYear, dealMonth, 0, 0L, 0L);
    }
}
