# 도토리(ACORN) · current-state

> 03_build: Overwrite Rule(지금 상태 1벌).

## Absorbed Planning
- `01_planning/01_feature/acorn_feature_spec.md` (AC-1~AC-6 전부 구현)
- `02_plan/01_feature/acorn_todos.md` (T1~T5 전부 완료)

## Runtime Assembly
- `AcornService.charge(user, amount, order_id=...)` → 잔액 증가, order_id 멱등, ledger 기록
- `AcornService.purchase(user, item_id, price, order_id=...)` → 잔액 부족 시 거부, 성공 시
  잔액 차감 + `inventory[user]`에 아이템 추가 + ledger 기록, order_id 멱등
- `AcornService.gift(sender, receiver, amount, order_id=...)` → 보내는 사용자 잔액 부족 시
  거부, 성공 시 양쪽 잔액 갱신(차감/증가) + 양쪽 ledger 기록, order_id 멱등
- `AcornService.ledger_for(user)` → 해당 사용자의 거래내역 목록(기록순)
- `shared/idem.IdempotencyStore` → charge/purchase/gift 공통 멱등 캐시

## Modules
| 모듈 | 책임 | AC |
| --- | --- | --- |
| `contexts/acorn/service.py` | 충전·구매·선물·잔액검증·거래내역 | 1·2·3·4·5·6 |
| `shared/idem.py` | order_id 기준 멱등 캐시 | 2·(모든 작업의 재실행 안전성) |

## Current Behavior
충전·구매·선물 모두 order_id당 한 번만 반영되고(재실행 시 replay=True로 최초 결과 반환),
모든 증감은 `ledger`에 `{user, type, amount, order_id, balance_after}`로 기록된다. 선물은
보내는 사용자 잔액이 수량보다 적으면 거부하고, 충분하면 양쪽 잔액을 갱신하며 양쪽에
`gift_sent`/`gift_received` 항목을 각각 남긴다.

## Not Yet Implemented
- 없음(계획된 AC-1~AC-6 전부 이번 슬라이스에서 구현·검증 완료).

## Residual Risk
- 잔액 부족으로 거부된 order_id(충전/구매/선물 공통)를 이후 잔액을 채운 뒤 같은 order_id로
  재시도하면, 멱등 캐시가 최초 거부 결과를 그대로 반환한다(재검증 없음). 실제 결제·선물
  재시도는 새 order_id 발급을 전제로 설계했다.
