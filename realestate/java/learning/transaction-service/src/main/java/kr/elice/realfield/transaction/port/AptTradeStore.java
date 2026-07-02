package kr.elice.realfield.transaction.port;

import kr.elice.realfield.common.AptTransaction;

import java.util.List;

/**
 * 거래원장 저장 포트입니다. 영속 기술(JPA)과 도메인 로직(멱등 적재)을 분리해, 멱등성 규칙을
 * DB 없이도 단위 테스트할 수 있게 합니다(헥사고날 포트/어댑터).
 */
public interface AptTradeStore {

    boolean existsByNaturalKey(String naturalKey);

    void save(AptTransaction transaction);

    List<AptTransaction> findByRegionMonth(String sggCd, int dealYear, int dealMonth);
}
