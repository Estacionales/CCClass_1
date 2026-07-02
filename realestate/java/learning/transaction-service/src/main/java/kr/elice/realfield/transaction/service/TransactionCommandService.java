package kr.elice.realfield.transaction.service;

import kr.elice.realfield.common.AptTransaction;
import kr.elice.realfield.transaction.port.AptTradeStore;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 거래 적재 커맨드 서비스입니다.
 *
 * <p>요구사항 AC-4(멱등): 동일 (시군구·계약월) 수집이 재실행돼도 자연키로 중복을 차단합니다.
 * 이미 존재하는 자연키는 건너뛰고, 새 거래만 저장한 뒤 새로 적재된 건수를 돌려줍니다.
 *
 * <p>범위 한계(의도된 것): 이번 턴의 멱등은 skip-if-exists입니다. 재수집으로 {@code canceled}
 * 상태가 바뀐 거래가 들어와도 기존 행을 덮어쓰지 않습니다(full upsert-with-update 아님).
 */
@Service
public class TransactionCommandService {

    private final AptTradeStore store;

    public TransactionCommandService(AptTradeStore store) {
        this.store = store;
    }

    /** 정규화된 거래 목록을 멱등 적재하고, 새로 들어간 건수를 반환합니다. */
    public int upsertAll(List<AptTransaction> transactions) {
        int inserted = 0;
        for (AptTransaction tx : transactions) {
            if (store.existsByNaturalKey(tx.naturalKey())) {
                continue; // 이미 적재된 거래입니다(멱등).
            }
            store.save(tx);
            inserted++;
        }
        return inserted;
    }

    /** 거래 원본 조회입니다. 분석 경계(T3)가 읽어가는 출처로, canceled 포함 전체를 반환합니다. */
    public List<AptTransaction> query(String sggCd, int dealYear, int dealMonth) {
        return store.findByRegionMonth(sggCd, dealYear, dealMonth);
    }
}
