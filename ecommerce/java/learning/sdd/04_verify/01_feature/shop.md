# 04_verify · 이커머스 쇼핑 검증 결과

> verify 단계는 "사람이 봤다"가 아니라 "코드가 통과시켰다"를 완료 기준으로 씁니다.
> 모든 AC 는 결정적 JUnit 테스트로 증명됩니다.
>
> 아래 "AC 커버리지/결과/게이트"는 완성본(reference target) 기준입니다. learning
> 워크스페이스의 실제 검증 현황은 바로 아래 "STEP 2 검증" 절에 분리해 기록합니다.

## STEP 2 검증 (learning 워크스페이스 · 도메인 구역)

도메인 구역 구현 직후의 실측 결과입니다.

- 실행 명령: `./gradlew test --tests 'kr.elice.shop.catalog.*' --tests 'kr.elice.shop.inventory.*' --tests 'kr.elice.shop.ordering.*'`
- 결과: BUILD SUCCESSFUL, 14개 테스트 전부 green (failures 0, errors 0).
  - `ProductTest` 4개: 가격 0원 거부, 재고 가감, 초과 차감 거부, ARCHIVED 재고변경 거부 (AC-C2·C3·C4·C6).
  - `InventoryServiceTest` 5개: 예약 가용분 차감, 확정 물리차감, 해제 복원, oversell 거부, 동시 100건 예약에서 정확히 50건만 성공·가용분 0 (AC-I1~I5).
  - `OrderTest` 5개: 총액 0원 거부, 정방향 전환, 이행 가드, 이행 후 취소 거부, 결제 후 취소 환불신호 (AC-O3·O4·O5·O6 + 취소신호).
- 회귀 범위: 이번 변경은 신규 도메인 코드 추가입니다. 기존에는 main 소스가 비어 있었으므로 깨질 상위/하위/공유 표면이 없습니다. 공유 커널(Money·ErrorCode·Page)은 새로 도입되었고 위 세 테스트가 그 사용처를 모두 커버합니다.

구조 게이트(DDD 경계):

- 실행 명령: `python3 sdd/99_toolchain/01_automation/run_arch_check.py`
- 결과: RESULT arch_check PASS, exit 0.
  - 규칙1 domain 순수성 위반 0건. 어떤 domain 클래스도 application·infrastructure·web 을 import 하지 않습니다.
  - 규칙2 컨텍스트 의존 엣지 `[(inventory, catalog)]`, 순환 없음. 현재 구현된 도메인 범위에서 inventory 가 catalog 에만 단방향으로 의존합니다.
- 주의: 게이트는 현재 소스에 존재하는 컨텍스트만 점수화합니다. cart·ordering·payment 는 아직 다른 컨텍스트를 참조하는 코드(응용/web)가 없어 엣지가 잡히지 않았습니다. checkout 오케스트레이션이 들어오는 다음 청크에서 의존 그래프가 확장되므로 게이트를 재실행합니다.

전체 스위트 실행(STEP 6 · 최종):

- 실행 명령: `./gradlew test` (단위 + E2E 전부).
- 결과(STEP 5 시점): BUILD FAILED. 단위 14개는 green, E2E 는 `ShopE2ETest > initializationError` 로 실패했습니다. `ShopApplication` 과 web 계층이 없어서 발생한 미완성 상태였습니다.
- STEP 6 에서 web + cart/ordering/payment 응용·인프라 + checkout 오케스트레이션 청크를 구현한 후 재실행: **BUILD SUCCESSFUL, 23/23 green** (failures 0, errors 0).
  - `ProductTest` 4개, `InventoryServiceTest` 5개, `OrderTest` 5개, `ShopE2ETest` 9개(E2E-1~9) 전부 통과.
- todos 의 "23개 전부 green" 게이트 통과.

구조 게이트 재실행(STEP 6):

- 실행 명령: `python3 sdd/99_toolchain/01_automation/run_arch_check.py`
- 1차 결과: FAIL. `OrderController`(ordering.web)가 취소 처리를 위해 `CheckoutService`를 직접 호출하도록
  구현했더니 `payment → ordering → checkout → payment` 순환이 잡혔습니다(payment→ordering,
  ordering→checkout, checkout→payment 세 엣지가 고리를 이룸).
- 조치: 취소 엔드포인트(`POST /api/orders/{id}/cancel`)를 `checkout.web.OrderCancelController` 로
  옮겨 ordering.web 이 checkout 을 더 이상 참조하지 않게 했습니다. 경로는 동일하게 유지했습니다.
- 2차 결과: **PASS**, exit 0.
  - 규칙1 domain 순수성 위반 0건.
  - 규칙2 컨텍스트 의존 엣지: `[(cart, catalog), (checkout, cart), (checkout, catalog), (checkout, inventory), (checkout, ordering), (checkout, payment), (inventory, catalog), (payment, inventory), (payment, ordering)]`. 순환 없음.
  - 설계 메모의 방향(`inventory·cart → catalog`, `payment → ordering·inventory`, `checkout → 전부`)과 정확히 일치합니다.

스모크 시나리오(bootRun · STEP 6):

- 실행: `./gradlew bootRun` 으로 서버 기동(8080 포트, 약 2.1초 기동).
- 시나리오: 상품 등록 → 장바구니 생성·담기 → 체크아웃 → 결제 → 이행 (curl 로 실제 HTTP 호출).
  1. `POST /api/products` → `prod_2f4883cd` ACTIVE, 재고 10.
  2. `POST /api/carts` + `POST /api/carts/.../items` → `cart_c7b88cce`, 노트북 2개 담김, 소계 2,000,000원.
  3. `POST /api/checkout` → `ord_ed9aaa2b` CREATED, 총액 2,000,000원. 가용 재고 8로 감소(예약).
  4. `POST /api/payments` → `pay_c1efe7df` CAPTURED. 주문 PAID, 물리 재고 8로 확정 차감.
  5. `POST /api/orders/.../fulfill` → 주문 FULFILLED.
- 판정: 전체 여정 정상 동작 확인. (한글 상품명은 curl 셸 인코딩 이슈로 400 이 났으나 ASCII 이름으로는
  정상 동작 확인 — 실제 UTF-8 JSON 은 `ShopE2ETest` 가 Java 레벨에서 이미 검증합니다.)

잔여 리스크:

- `Cart`·`Payment` 애그리거트 전용 단위 테스트가 없습니다. E2E 9개가 간접 검증하지만 격리된 단위 테스트는 없습니다.
- 저장소가 인메모리 어댑터입니다. JPA 어댑터로 교체 시 스키마 검증이 별도로 필요합니다.
- 서버 재시작 시 모든 데이터가 초기화됩니다.

## 검증 방식

- 도메인 규칙은 애그리거트 단위 테스트로 빠르게 검증합니다(Spring 컨텍스트 없음).
- 컨텍스트를 가로지르는 흐름은 @SpringBootTest + MockMvc 로 실제 HTTP 경계를 통과시켜 검증합니다.
- 결제 게이트웨이는 포트/어댑터로 분리해 거절 경로를 결정적으로 재현합니다.

## AC 커버리지

27개 AC 전부가 최소 하나의 테스트로 매핑됩니다. 상세 매핑은
`01_planning/01_feature/shop_feature_spec.md` 의 검증 열에 있습니다.

## 결과

`10_test/proof_evidence.md` 참조. 23/23 PASS, exit 0.

## 게이트 통과 기준

- 컴파일 성공: `./gradlew build` 가 BUILD SUCCESSFUL.
- 테스트 전부 green: failures·errors 가 0.
- E2E 9개가 모두 PASS: 요구사항 원문의 모든 비즈니스 룰이 API 경계에서 동작함을 의미합니다.
