# T2 · 거래원장(transaction-service) · 구현 요약 (03_build)

> SDD 'build' 산출물. current-state only — dated execution narrative 금지.
> 대상 위치: `sdd/03_build/01_feature/03_t2_transaction.md`
> 상태: 확정 — 오케스트레이션 세션이 전체 리포지토리 기준으로 빌드를 독립 재실행해 검증했다(§검증 참조).

## 구현 범위
- 구현한 기능/경계:
  - 헥사고날 포트/어댑터: `AptTradeStore`(포트)로 도메인 멱등 로직과 영속 기술(JPA)을 분리해,
    멱등성 규칙을 DB 없이 인메모리 스텁으로 단위 검증할 수 있게 한다.
  - `JpaAptTradeStore`(어댑터) + `AptTradeRepository`(Spring Data) + `AptTradeEntity`(엔티티)로
    포트를 H2 영속에 연결한다.
  - `TransactionCommandService.upsertAll(...)` 멱등 적재: 자연키가 이미 있으면 건너뛰고 새 거래만
    저장한 뒤 **새로 삽입된 건수**를 반환한다(AC-4). 같은 (시군구·계약월) 재수집이 중복을 만들지 않는다.
  - 거래 원본 조회(`TransactionCommandService.query(...)` → `AptTradeStore.findByRegionMonth(...)`):
    분석 경계(T3)가 읽어가는 출처. `canceled` 여부와 무관하게 해당 시군구·계약월 전체를 반환한다.
- 멱등 이중 방어: 애플리케이션 레벨 `existsByNaturalKey` 선검사 + DB 레벨 자연키 유니크 제약
  (`uk_apt_trade_natural`)을 함께 둔다. 앱 체크가 정상 경로의 중복을 걸러내고, 유니크 제약이
  경합/우회 삽입까지 DB 차원에서 최종 차단한다.

## 변경 모듈
- transaction-service (이 트랙이 만진 유일한 모듈):
  - `kr.elice.realfield.transaction.port.AptTradeStore` — 저장 포트 인터페이스.
    `existsByNaturalKey(String):boolean`, `save(AptTransaction):void`,
    `findByRegionMonth(String,int,int):List<AptTransaction>`. pin된 `IdempotentUpsertTest`의
    인메모리 스텁과 동일 계약.
  - `kr.elice.realfield.transaction.adapter.AptTradeEntity` — 거래원장 영속 엔티티.
    `@Entity @Table(name="apt_trade", uniqueConstraints=@UniqueConstraint(name="uk_apt_trade_natural",
    columnNames="natural_key"))`. `common.AptTransaction`의 11필드 + 파생 `natural_key` 컬럼을 보관.
    `from(AptTransaction)`(정적 팩터리) / `toDomain()`(역변환) 제공 — 도메인 record와 엔티티의 경계 변환.
  - `kr.elice.realfield.transaction.adapter.AptTradeRepository` — `JpaRepository<AptTradeEntity,Long>`.
    파생 쿼리 `existsByNaturalKey`, `findBySggCdAndDealYearAndDealMonth`.
  - `kr.elice.realfield.transaction.adapter.JpaAptTradeStore` — `@Repository`, `AptTradeStore` 구현.
    리포지토리에 위임하고 엔티티↔도메인 변환을 담당.
  - `kr.elice.realfield.transaction.service.TransactionCommandService` — `@Service`, 생성자 주입.
    `upsertAll`(멱등 적재), `query`(원본 조회).
  - `build.gradle` 변경 없음(`spring-boot-starter-data-jpa`·`h2` 이미 존재).
  - `application.yml` 변경 없음(H2 인메모리 + `ddl-auto: create-drop` 이미 설정됨).
- common / ingestion-service / analytics-service / api-gateway / config-server / service-discovery: 변경 없음.

## 계약·자산
- 소비한 데이터 계약: `common.AptTransaction`(11필드 record)과 그 `naturalKey()`(9필드 조합) 인스턴스
  메서드를 그대로 소비한다. 표준 스키마를 재정의하지 않았고 `common/**`은 손대지 않았다.
- 영속 스키마(자산): `apt_trade` 테이블. 도메인 11필드 컬럼 + `id`(IDENTITY PK) + `natural_key`
  (`length=300`, `nullable=false`, 유니크 제약).
- 자연키 유니크 형태 드리프트: 계획서(`02_plan` 체크리스트)는 "자연키 9개 컬럼 **복합** 유니크 제약"을
  적었으나, 실제 구현은 `common.AptTransaction.naturalKey()`가 만든 **단일 파생 문자열 컬럼**
  `natural_key`에 유니크 제약을 건다. 두 방식은 동일한 9개 필드로 유일성을 보장하지만 형태가 다르다.
  pin된 `IdempotentUpsertTest`와 참조 답안이 파생 문자열 키 방식을 정본으로 고정했고, 멱등 계약
  (`existsByNaturalKey(String)`)이 문자열 키를 전제로 하므로 이 형태를 따랐다.
- 저장 필드 범위 드리프트(T1과 동일 계열): 엔티티는 `common.AptTransaction`의 11필드만 저장한다.
  계획서 AC-1이 참조한 `04_data` §1.1 전체 필드(umdCd·jibun·aptSeq·aptDong·slerGbn·buyerGbn·
  estateAgentSggNm·landLeaseholdGbn·rgstDate·**canceledDate** 등)보다 좁다. 특히 `canceledDate`는
  현재 계약(record)에 없어 엔티티에도 없다. 이는 `02_t1_ingestion.md`에 이미 기록된 계약 축소 드리프트를
  그대로 계승한 것이다(본 트랙이 새로 만든 드리프트가 아님, `common` 미변경).

## 현재 사용자 가시 동작
- REST 엔드포인트·부트스트랩 클래스가 없어 외부에서 관측 가능한 동작은 아직 없다.
- 내부적으로는 `List<AptTransaction>` → 멱등 적재(신규 건수 반환) → 시군구·계약월 조회 경로가 조립 가능하다.
- 모듈은 아직 실제로 부팅되지 않는다(`@SpringBootApplication` 부트스트랩 없음) — 이는 `ingestion-service`와
  동일한 현재 상태이며 본 턴의 의도된 범위다(REST/부트스트랩 미요청).

## 본 턴에서 구현하지 않은 T2 범위(명시적 범위 밖 / 의도된 한계)
- **멱등 = skip-if-exists (의도된 스코프 한계)**: 이번 턴의 멱등은 "존재하면 건너뜀"이다. 재수집으로
  `canceled` 상태가 정상→해제로 바뀐 거래가 들어와도 **기존 행을 덮어쓰지 않는다**. 즉 full
  upsert-with-field-update가 아니다. 계획서 AC-1/AC-4의 "충돌 건은 갱신"과 CONR-005(정상→해제 전환
  반영)는 이 설계에서 **아직 충족하지 않는다**. 조용히 확장하지 않고 여기 명시한다.
- `POST /internal/transactions/batch-upsert` 컨트롤러(`05_api` §3b: `receivedCount`/`createdCount`/
  `updatedCount`) — 미구현(REST 계층 미요청).
- `GET /api/v1/transactions` 컨트롤러(`05_api` §3: `sggCd`+`dealYm` 파라미터, 페이징, 정렬) — 미구현.
  현재 조회는 서비스 메서드 `query(...)`까지만 존재하고 HTTP 표면은 없다.
- `TransactionApplication`(`@SpringBootApplication`) 부트스트랩 — 미요청, 미생성.
- `canceledDate` 컬럼 매핑 — 계약(record)에 필드가 없어 미보관(위 드리프트 참조).

## H2 스키마 학습용 제약 (현재 상태 기록)
- `ddl-auto: create-drop` + `jdbc:h2:mem:realfield`(인메모리)로 기동 시 스키마를 생성하고 종료 시 폐기한다.
  학습·테스트 편의를 위한 설정이며, 유니크 제약(`uk_apt_trade_natural`)도 이 create-drop 스키마에서만
  존재한다. 운영 전환 시에는 영속 DB + 스키마 마이그레이션(Flyway/Liquibase 등)과 유니크 제약의
  영구 정의가 필요하다 — **본 트랙 범위 밖, 후속 과제로만 남긴다**.

## 검증한 회귀 범위
- 직접: `./gradlew :transaction-service:test` → BUILD SUCCESSFUL.
  - `IdempotentUpsertTest.reingestionDoesNotDuplicate` (AC-4): 동일 배치 1회차 1건 삽입, 2회차 0건,
    원장에 1건만 잔존 — 통과.
- 구조 게이트: `python sdd/99_toolchain/01_automation/run_arch_check.py` → RESULT: PASS (7/7).
  본 트랙 관련 규칙 "transaction-service → common 의존"이 PASS로 전환됐다(이전 FAIL 원인은 메인 소스
  부재였고, 본 턴의 포트/어댑터/서비스 추가로 해소).
- 미검증(범위 밖): REST 계층·부트스트랩이 없어 실제 HTTP·컨텍스트 기동 경로는 검증 대상이 아니다.
- 오케스트레이션 세션 독립 재검증(T2/T3/T4 병렬 트랙 완료 후, 전체 리포지토리 기준): `./gradlew test`
  전 모듈 BUILD SUCCESSFUL(공유 `common.AptTransaction.buildYear`를 `Integer`→`int`로 정정한 뒤 재확인
  포함 — T2의 `AptTradeEntity` int 필드 대입과 정합), `run_arch_check.py` 7/7 PASS 재확인.
