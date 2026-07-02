package kr.elice.realfield.transaction.adapter;

import jakarta.persistence.*;
import kr.elice.realfield.common.AptTransaction;

/** 거래원장 영속 엔티티입니다. 자연키에 유니크 제약을 걸어 DB 차원에서도 중복을 막습니다. */
@Entity
@Table(name = "apt_trade",
        uniqueConstraints = @UniqueConstraint(name = "uk_apt_trade_natural", columnNames = "natural_key"))
public class AptTradeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "natural_key", nullable = false, length = 300)
    private String naturalKey;

    private String sggCd;
    private String umdNm;
    private String aptNm;
    private double exclusiveArea;
    private int floor;
    private int buildYear;
    private int dealYear;
    private int dealMonth;
    private int dealDay;
    private long dealAmountWon;
    private boolean canceled;

    protected AptTradeEntity() {}

    public static AptTradeEntity from(AptTransaction tx) {
        AptTradeEntity e = new AptTradeEntity();
        e.naturalKey = tx.naturalKey();
        e.sggCd = tx.sggCd();
        e.umdNm = tx.umdNm();
        e.aptNm = tx.aptNm();
        e.exclusiveArea = tx.exclusiveArea();
        e.floor = tx.floor();
        e.buildYear = tx.buildYear();
        e.dealYear = tx.dealYear();
        e.dealMonth = tx.dealMonth();
        e.dealDay = tx.dealDay();
        e.dealAmountWon = tx.dealAmountWon();
        e.canceled = tx.canceled();
        return e;
    }

    public AptTransaction toDomain() {
        return new AptTransaction(sggCd, umdNm, aptNm, exclusiveArea, floor, buildYear,
                dealYear, dealMonth, dealDay, dealAmountWon, canceled);
    }
}
