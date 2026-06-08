package kr.elice.realfield.ingestion.client;

import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * 오프라인 실습·E2E용 스텁 원천입니다. data.go.kr 실호출 없이 결정적 캔드 응답을 돌려줍니다.
 * {@code stub} 프로필에서 활성화되어, 서비스 부팅 E2E를 네트워크·인증키 없이 멱등하게 만듭니다.
 *
 * <p>서울 종로구(11110) 2024년 5월 표본: 정상 4건 + 해제 1건. 정상 거래금액(만원)은
 * 70,000 / 80,000 / 90,000 / 100,000 이고 해제 1건(cdealType=O)은 집계에서 빠지므로,
 * 중위 거래금액은 (80,000 + 90,000)/2 = 85,000만원 = 850,000,000원으로 결정적입니다.
 */
@Component
@Profile("stub")
public class StubAptTradeSource implements AptTradeSource {

    @Override
    public List<MolitAptTradeItem> fetchAptTrades(String lawdCd, String dealYmd) {
        // 인자 순서: sggCd, umdNm, jibun, aptNm, excluUseAr, dealYear, dealMonth, dealDay,
        //            dealAmount, floor, buildYear, dealingGbn, cdealType, cdealDay
        return List.of(
            new MolitAptTradeItem("11110", "청운동", "123", "경복궁아파트", "84.97", "2024", "5", "10", " 70,000", "5", "2003", "중개거래", null, null),
            new MolitAptTradeItem("11110", "청운동", "124", "경복궁아파트", "84.97", "2024", "5", "12", " 80,000", "10", "2003", "중개거래", null, null),
            new MolitAptTradeItem("11110", "사직동", "200", "사직파크", "59.94", "2024", "5", "15", " 90,000", "8", "2010", "직거래", null, null),
            new MolitAptTradeItem("11110", "사직동", "201", "사직파크", "59.94", "2024", "5", "18", "100,000", "12", "2010", "중개거래", null, null),
            new MolitAptTradeItem("11110", "청운동", "125", "경복궁아파트", "84.97", "2024", "5", "20", "999,999", "9", "2003", "중개거래", "O", "24.06.01")
        );
    }
}
