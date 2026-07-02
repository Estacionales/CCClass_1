package kr.elice.realfield.transaction.adapter;

import kr.elice.realfield.common.AptTransaction;
import kr.elice.realfield.transaction.port.AptTradeStore;
import org.springframework.stereotype.Repository;

import java.util.List;

/** {@link AptTradeStore} 포트의 JPA 어댑터입니다. 도메인 멱등 로직과 영속 기술을 연결합니다. */
@Repository
public class JpaAptTradeStore implements AptTradeStore {

    private final AptTradeRepository repository;

    public JpaAptTradeStore(AptTradeRepository repository) {
        this.repository = repository;
    }

    @Override
    public boolean existsByNaturalKey(String naturalKey) {
        return repository.existsByNaturalKey(naturalKey);
    }

    @Override
    public void save(AptTransaction transaction) {
        repository.save(AptTradeEntity.from(transaction));
    }

    @Override
    public List<AptTransaction> findByRegionMonth(String sggCd, int dealYear, int dealMonth) {
        return repository.findBySggCdAndDealYearAndDealMonth(sggCd, dealYear, dealMonth)
                .stream().map(AptTradeEntity::toDomain).toList();
    }
}
