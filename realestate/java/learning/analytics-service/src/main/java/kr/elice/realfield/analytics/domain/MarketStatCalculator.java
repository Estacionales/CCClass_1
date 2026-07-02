package kr.elice.realfield.analytics.domain;

import kr.elice.realfield.common.AptTransaction;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * 거래 목록에서 시세 통계를 계산하는 순수 도메인 로직입니다.
 *
 * <p>요구사항 AC-3: 해제된 거래({@code canceled})는 집계에서 제외합니다.
 * 요구사항 AC-5: 거래원장 원본이 아니라 이 집계 결과(read model)를 조회 응답으로 돌려줍니다.
 *
 * <p>결정성: 같은 입력이면 항상 같은 통계를 낸다(정렬 기반 중위값, 부동소수 누적 없음).
 */
@Component
public class MarketStatCalculator {

    public MarketStat calculate(String sggCd, int dealYear, int dealMonth, List<AptTransaction> transactions) {
        List<AptTransaction> valid = transactions.stream()
                .filter(t -> !t.canceled())   // AC-3: 해제거래 제외
                .toList();

        if (valid.isEmpty()) {
            return MarketStat.empty(sggCd, dealYear, dealMonth);
        }

        long medianPrice = median(valid.stream().mapToLong(AptTransaction::dealAmountWon).sorted().toArray());
        long medianPerM2 = median(valid.stream().mapToLong(AptTransaction::pricePerSquareMeter).sorted().toArray());

        return new MarketStat(sggCd, dealYear, dealMonth, valid.size(), medianPrice, medianPerM2);
    }

    /** 정렬된 배열의 중위값을 반환합니다(짝수면 두 가운데 값의 평균). */
    private long median(long[] sorted) {
        int n = sorted.length;
        if (n == 0) return 0L;
        if (n % 2 == 1) return sorted[n / 2];
        return (sorted[n / 2 - 1] + sorted[n / 2]) / 2;
    }
}
