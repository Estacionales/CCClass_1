# 02_plan · 이커머스 쇼핑 todos

> EARS 명세를 구현 가능한 작업 단위로 분해합니다. Execution Checklist 의 각 구역은
> 서로 의존성이 낮아 병렬로 잡을 수 있습니다. 구역 하나가 대략 PR 하나에 대응됩니다.

## 현재 진행 노트 (learning 워크스페이스)

아래 Execution Checklist 의 `[x]` 표시는 완성본 기준입니다. 이 learning 워크스페이스는
실습용 init 상태로 시작했고(main 소스 비어 있음, 테스트만 존재), 단계별로 다시 구현합니다.

- STEP 2 에서 도메인 구역(구역 1 공유 커널, 구역 2~6 의 도메인 계층 + 단위 테스트가 직접 쓰는 CatalogService·InventoryService 와 catalog·inventory 인메모리 어댑터)을 구현했습니다. 14개 도메인 단위 테스트가 green 입니다.
- STEP 6 에서 나머지 청크(cart·ordering·payment 의 응용/인프라, checkout 오케스트레이션, 전 컨텍스트 web 계층, `ShopApplication`, `DemoPaymentGateway`)를 구현해 21개 REST 엔드포인트를 모두 노출했습니다. `./gradlew test` 로 단위 14 + E2E 9 = 23개 전부 green 을 확인했습니다.
- 취소(`POST /api/orders/{id}/cancel`)는 예약 해제·결제 환불 보상이 필요해 `checkout.web.OrderCancelController` 가 처리합니다(경로는 `/api/orders/{id}/cancel` 로 ordering 표면과 동일). `OrderController` 에 그대로 두면 `ordering → checkout → payment → ordering` 순환 의존이 생겨 `run_arch_check.py` 가 실패하기 때문입니다.
- 빌드/검증 현재 상태는 `03_build/01_feature/shop.md` 와 `04_verify/01_feature/shop.md` 에 기록했습니다.

## Acceptance Criteria 체크리스트

| AC | 설명 | 테스트 |
| --- | --- | --- |
| AC-C2 | 가격 0원 이하 거부 | ProductTest |
| AC-C4 | 재고 부족 차감 거부 | ProductTest |
| AC-C6 | ARCHIVED 재고변경 거부 | ProductTest |
| AC-I4 | oversell 예약 거부 | InventoryServiceTest, E2E-4 |
| AC-I5 | 동시성 oversell 방지 | InventoryServiceTest |
| AC-O2 | 체크아웃 보상 해제 | E2E-4 |
| AC-O5 | 결제 전 이행 거부 | E2E-8 |
| AC-P2 | 결제 거절 처리 | E2E-9 |
| AC-P4 | 취소 시 환불·복원 | E2E-3 |

## Execution Checklist

### 1. 공유 커널 (shared)
- [x] Money 값 객체를 만든다. 음수 금지, plus·times 연산을 제공한다.
- [x] ErrorCode 와 HTTP 상태 매핑, DomainException, 전역 예외 핸들러를 만든다.
- [x] Page 공용 페이징 값 객체를 만든다.

### 2. 상품 컨텍스트 (catalog)
- [x] Product 애그리거트와 ProductStatus 를 만든다. 가격·재고·상태 불변식을 애그리거트에 모은다.
- [x] ProductRepository 포트와 인메모리 어댑터를 만든다.
- [x] CatalogService 에 등록(멱등)·조회·검색/페이징·재고가감·아카이브를 구현한다.
- [x] ProductController 로 REST 표면을 노출한다.

### 3. 재고 컨텍스트 (inventory)
- [x] Reservation 애그리거트와 상태(RESERVED·CONFIRMED·RELEASED)를 만든다.
- [x] InventoryService 에 reserve·confirm·release 와 available 계산을 구현한다.
- [x] reserve 를 동기화해 동시 예약에서도 oversell 을 막는다.

### 4. 장바구니 컨텍스트 (cart)
- [x] Cart 애그리거트에 담기·수량변경·삭제·비우기를 구현한다.
- [x] CartService 에서 ARCHIVED 상품 담기를 막는다.
- [x] CartController 와 가격 스냅샷 뷰를 제공한다.

### 5. 주문 컨텍스트 (ordering)
- [x] Order 애그리거트에 상태머신(CREATED→PAID→FULFILLED, CANCELLED)을 구현한다.
- [x] OrderLine 으로 가격 스냅샷을 고정한다.
- [x] OrderService 와 OrderController(목록·단건·이행·취소)를 만든다.

### 6. 결제 컨텍스트 (payment)
- [x] Payment 애그리거트와 게이트웨이 포트를 만든다. 데모 어댑터는 결정적으로 동작한다.
- [x] PaymentService 에 결제(멱등·예약확정·주문 PAID)와 환불을 구현한다.
- [x] PaymentController 로 결제·조회·환불을 노출한다.

### 7. 체크아웃 오케스트레이션 (checkout)
- [x] CheckoutService 에 장바구니→예약→주문 흐름과 실패 시 보상 해제를 구현한다.
- [x] 취소 보상(예약 해제 + 결제 환불)을 구현한다.
- [x] CheckoutController 로 체크아웃을 노출한다.

### 8. 검증 (verify)
- [x] 도메인 단위 테스트(ProductTest·OrderTest·InventoryServiceTest)를 작성한다.
- [x] @SpringBootTest + MockMvc E2E 9개 시나리오를 작성한다.
- [x] ./gradlew build 로 23개 전부 green 을 확인한다.
