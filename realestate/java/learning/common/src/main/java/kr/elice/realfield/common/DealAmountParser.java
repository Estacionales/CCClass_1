package kr.elice.realfield.common;

/**
 * DAR-002 정합 규칙의 유일한 강제 지점: 거래금액(만원 단위 콤마 문자열) → 원 단위 정수(long).
 *
 * <p>선행 공백·천 단위 콤마 제거 → 만원 정수 → ×10000. 이 변환은 오직 여기 한곳에만 둔다.
 * 수집(ingestion)·분석(analytics) 어디서도 콤마 제거/×10000 로직을 재구현하지 않는다
 * (데이터명세서 §3.1, §5 품질 게이트).
 */
public final class DealAmountParser {

    private static final long MAN_WON = 10_000L;

    private DealAmountParser() {
    }

    /**
     * {@code "  82,500"} 형태의 만원 문자열을 원 단위 long으로 변환한다.
     *
     * @throws IllegalArgumentException null·공백·비숫자 문자열이거나 변환 결과가 0 이하일 때.
     *         (품질 게이트 위반은 조용히 0으로 대체하지 않고 신호를 준다 — 호출부가 스킵·사유 기록한다.)
     */
    public static long toWon(String rawDealAmount) {
        if (rawDealAmount == null) {
            throw new IllegalArgumentException("거래금액이 null 입니다");
        }
        String cleaned = rawDealAmount.replace(",", "").trim();
        if (cleaned.isEmpty()) {
            throw new IllegalArgumentException("거래금액이 비어 있습니다");
        }

        long manWon;
        try {
            manWon = Long.parseLong(cleaned);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("거래금액을 숫자로 변환할 수 없습니다: [" + cleaned + "]");
        }
        if (manWon <= 0) {
            throw new IllegalArgumentException("거래금액이 0 이하입니다: " + manWon);
        }
        return manWon * MAN_WON;
    }
}
