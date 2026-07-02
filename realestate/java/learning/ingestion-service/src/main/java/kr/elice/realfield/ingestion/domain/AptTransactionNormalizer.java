package kr.elice.realfield.ingestion.domain;

import kr.elice.realfield.common.AptTransaction;
import kr.elice.realfield.common.DealAmountParser;
import kr.elice.realfield.ingestion.client.MolitAptTradeItem;
import org.springframework.stereotype.Component;

/**
 * 원천 XML item 1건 → 표준 {@link AptTransaction} 정규화({@code 04_data} §1.1).
 *
 * <p>금액 정합(DAR-002)은 {@link DealAmountParser} 한곳에만 위임한다 — 이 클래스는 콤마 제거/×10000을
 * 재구현하지 않는다. 품질 게이트(데이터명세서 §5) 위반(금액 파싱 실패·필수 숫자 결측·면적 0 이하)은
 * 조용히 0으로 대체하지 않고 {@link IllegalArgumentException}으로 신호를 준다(fetch 실패와 마찬가지로
 * 예외를 밖으로 흘리지 않는 fetch 경계와 달리, 정규화 실패는 호출부가 건별로 스킵·사유 기록한다).
 *
 * <p>{@code common.AptTransaction}이 pin된 11필드 계약(jibun·dealingGbn·canceledDate 미포함)이라
 * 이 정규화기도 그 범위로 매핑한다. {@code cdealDay}(해제사유발생일)는 현재 계약에 저장할 필드가
 * 없어 {@code canceled} 판정에만 쓰고 버린다 — 알려진 드리프트(03_build 참조).
 */
@Component
public class AptTransactionNormalizer {

    public AptTransaction normalize(MolitAptTradeItem item) {
        // 금액 정규화는 common 계약 한곳에서만 강제한다(DAR-002). 실패 시 IllegalArgumentException 전파.
        long dealAmountWon = DealAmountParser.toWon(item.dealAmount());

        double exclusiveArea = parseRequiredDouble(item.excluUseAr(), "전용면적");
        if (exclusiveArea <= 0) {
            throw new IllegalArgumentException("전용면적이 0 이하입니다: " + item.excluUseAr());
        }

        boolean canceled = item.cdealType() != null && item.cdealType().trim().equals("O");

        return new AptTransaction(
                trim(item.sggCd()),
                trim(item.umdNm()),
                trim(item.aptNm()),
                exclusiveArea,
                parseRequiredInt(item.floor(), "층"),
                parseIntOrZero(item.buildYear()),
                parseRequiredInt(item.dealYear(), "계약년도"),
                parseRequiredInt(item.dealMonth(), "계약월"),
                parseRequiredInt(item.dealDay(), "계약일"),
                dealAmountWon,
                canceled);
    }

    private static String trim(String s) {
        return s == null ? null : s.trim();
    }

    private static double parseRequiredDouble(String raw, String fieldName) {
        if (raw == null || raw.trim().isEmpty()) {
            throw new IllegalArgumentException(fieldName + " 필수 항목이 비어 있습니다");
        }
        // NumberFormatException은 IllegalArgumentException의 하위 타입 — 스킵 신호로 일관 처리된다.
        return Double.parseDouble(raw.trim());
    }

    private static int parseRequiredInt(String raw, String fieldName) {
        if (raw == null || raw.trim().isEmpty()) {
            throw new IllegalArgumentException(fieldName + " 필수 항목이 비어 있습니다");
        }
        return Integer.parseInt(raw.trim());
    }

    /**
     * {@code buildYear}는 {@code common.AptTransaction}에서 primitive {@code int}다(결측을 표현할
     * null이 없다) — 결측(공백)이면 0으로 채운다. CONR-004/DAR-006이 원하는 진짜 결측 보존(null)은
     * 이 필드가 primitive로 고정된 이상 표현할 수 없다 — 알려진 드리프트(03_build 참조).
     */
    private static int parseIntOrZero(String raw) {
        if (raw == null || raw.trim().isEmpty()) {
            return 0;
        }
        return Integer.parseInt(raw.trim());
    }
}
