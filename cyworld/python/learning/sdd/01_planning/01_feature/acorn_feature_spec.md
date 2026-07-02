# 도토리(ACORN) · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 원문: `sdd/00_sources/02_requirements/acorn-currency.md`
> 실 결제 연동 없음(가상 스텁). [[minihomepy_feature_spec]]의 스킨/BGM 적용이 여기 인벤토리에
> 의존한다.

**AC-1** When 사용자가 결제 요청으로 도토리 충전을 요청하면, the system shall 결제 금액에
해당하는 도토리를 계정 잔액에 반영하고 거래내역을 기록한다.

**AC-2** When 동일한 결제 요청(idempotency key)이 재실행되면, the system shall 중복
충전 없이 기존 결과를 반환한다.

**AC-3** While 잔액이 아이템 가격보다 적을 때, when 아이템 구매를 요청하면, the system
shall 구매를 거부한다.

**AC-4** When 도토리로 아이템을 구매하면, the system shall 잔액을 차감하고 해당 아이템을
사용자 인벤토리에 추가한다.

**AC-5** When 사용자가 다른 사용자에게 도토리를 선물하면, the system shall 보내는
사용자의 잔액을 차감하고 받는 사용자의 잔액을 동일 수량만큼 증가시키며 양쪽 거래내역을
기록한다.

**AC-6** While 선물 수량이 보유 잔액을 초과할 때, when 선물을 요청하면, the system shall
선물을 거부한다.

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1·AC-2 | `tests/test_acorn.py::test_charge_idempotent` |
| AC-3·AC-4 | `tests/test_acorn.py::test_purchase_updates_inventory` |
| AC-5·AC-6 | `tests/test_acorn.py::test_gift_balance_transfer` |
| 회귀 | `tests/test_regression.py` (minihomepy 인벤토리 조회 포함) |
