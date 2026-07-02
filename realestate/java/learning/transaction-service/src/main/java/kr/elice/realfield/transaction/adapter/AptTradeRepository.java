package kr.elice.realfield.transaction.adapter;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

/** JPA 리포지토리입니다. 자연키 존재 확인과 시군구·계약월 조회를 제공합니다. */
public interface AptTradeRepository extends JpaRepository<AptTradeEntity, Long> {

    boolean existsByNaturalKey(String naturalKey);

    List<AptTradeEntity> findBySggCdAndDealYearAndDealMonth(String sggCd, int dealYear, int dealMonth);
}
