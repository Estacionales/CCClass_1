package kr.elice.realfield.ingestion.client;

/**
 * 한 페이지 수집 시도의 결과 래퍼.
 *
 * <p>재시도 소진·서킷 오픈 등 외부 장애를 수집 경계 안에 가두기 위한 타입이다(AC-2).
 * fetch에 성공하면 {@code fetched=true}와 응답을 담고, 실패하면 {@code fetched=false}와 사유를 담는다.
 * fallback이 raw 예외를 밖으로 흘리지 않으므로, 호출부는 예외 없이 "이 페이지는 수집 실패"를 판정할 수 있다.
 */
public record MolitFetchResult(boolean fetched, MolitAptTradeResponse response, String failureReason) {

    public static MolitFetchResult ok(MolitAptTradeResponse response) {
        return new MolitFetchResult(true, response, null);
    }

    public static MolitFetchResult failed(String failureReason) {
        return new MolitFetchResult(false, null, failureReason);
    }
}
