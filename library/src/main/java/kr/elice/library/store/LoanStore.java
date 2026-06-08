package kr.elice.library.store;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import kr.elice.library.domain.Loan;
import org.springframework.stereotype.Component;

/** 대출 공유 저장소입니다. 레거시·신규 대출 구현이 같은 대출 데이터를 봅니다. */
@Component
public class LoanStore {

    private final Map<String, Loan> rows = new ConcurrentHashMap<>();
    private final AtomicLong seq = new AtomicLong(0);

    public String nextId() {
        return "loan_" + seq.incrementAndGet();
    }

    public Loan save(Loan loan) {
        rows.put(loan.id(), loan);
        return loan;
    }

    public Optional<Loan> find(String id) {
        return Optional.ofNullable(rows.get(id));
    }

    public List<Loan> activeByMember(String memberId) {
        return rows.values().stream()
                .filter(l -> l.memberId().equals(memberId))
                .filter(Loan::isActive)
                .toList();
    }
}
