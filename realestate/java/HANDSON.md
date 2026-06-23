# 부동산 대규모 MSA 핸즈온 (15·16강)

> 실재하는 공개 데이터(data.go.kr 국토교통부 실거래가)를 소재로, 대규모 Spring Cloud MSA를
> **Claude Code 발화만으로** SDD 5단계로 끌고 갑니다. 15강은 요구사항 정제와 아키텍처 판단(Stage 1~3),
> 16강은 병렬 구현과 검증(Stage 4)입니다. 모든 단계는 **몇 번이든 같은 결과로 반복(멱등)** 됩니다.

## 준비

실습은 시작 상태인 `learning/` 에서 출발합니다. `init/` 은 손대지 않는 시작 보관본이고,
완성본 대조는 옆 `complete/` 를 봅니다.
```bash
git clone https://github.com/say828/agentic-dev-demo.git
cd agentic-dev-demo/realestate/java/learning
claude                       # Claude Code 실행 (.claude/skills/sdd 자동 적용)
```

실습 하네스 `lab.sh`로 시작 상태와 정답을 오갑니다. 발화 실습은 reset에서 출발합니다.
```bash
./lab.sh status        # 코드·15강 산출물·web 구현 존재 여부
./lab.sh reset         # 코드 7개 모듈(도메인+인프라)의 src/main/java 를 비운 시작 상태
./lab.sh verify        # 아키텍처 게이트(7) + gradle 단위 테스트(8개)
./lab.sh solve         # 정답 코드 복원 (라이브 폴백·완성본 확인)
./lab.sh solve stage3  # 15강 산출물(01_planning+02_plan) 복원 (16강만 새로 시작할 때)
```
- 빌드 환경: **JDK 17 + Gradle 래퍼**(`./gradlew`). 인증키는 런타임에만 필요하고, 단위 검증은 네트워크 없이 결정적입니다.
- `reset → 발화로 구현 → verify → reset`을 반복해도 매번 **아키텍처 게이트 PASS(7/7) + 단위 8/8**로 수렴합니다.

---

## 15강 · Stage 1~3 : 요구사항에서 아키텍처 판단, 비중첩 플랜까지

> 주어지는 것은 `sdd/00_sources` 의 발주 입력 세 벌입니다.
> 요구사항정의서(`02_requirements/realfield-부동산실거래.md`, SFR·DAR·PER·SIR·SECR·CONR),
> 외부 API 공개명세(`01_apis/molit_apt_trade_api.md`, data.go.kr 실거래 상세 자료),
> 데이터 명세서(`03_data_spec/realprice_data_spec.md`, 항목 사전·코드 도메인·표기 규칙)입니다.
> 시작 상태(`learning/`·`init/`)에는 `00_sources` 만 있고 `01_planning`·`02_plan`은 비어 있습니다.
> 학습자가 발화로 `01_planning` → `02_plan`을 생성합니다. 막히면 `complete/` 와 대조하거나
> `./lab.sh solve stage3` 로 정답 산출물을 복원합니다.

### Stage 1 · 구조화 (00_sources → 01_planning)
```
> 00_sources 의 요구사항정의서·API 공개명세·데이터 명세서를 읽고 SDD로 구조화해줘.
  기능을 01_planning/01_feature 에 EARS(AC-1~AC-5)로, 비기능을 08_nonfunctional,
  보안을 09_security 로. 데이터 정합(콤마 금액 변환·해제거래 제외)을 수용기준으로 박아줘.
```
확인: AC-1~AC-5가 판정 가능한 EARS인가, AC-3에 콤마 금액·해제 제외가 있는가.

### Stage 2 · 아키텍처링 (사람이 판단)
먼저 토론합니다. 읽기·쓰기 부하가 다른가(CQRS?), 외부 API 장애를 어디에 가둘까, 지금 비동기가 필요한가.
```
> 이 서비스 특성을 고려해 MSA 경계를 01_planning/03_architecture 에 설계하고,
  각 경계 결정의 근거와 기각한 대안을 함께 남겨줘.
  이어서 04_data, 05_api, 07_integration(data.go.kr 연계 계약)도 작성해줘.
```
확인: bounded context가 MECE한가, 모듈 경계가 비중첩인가, **결정 근거가 남았는가**.
라이브가 막히면 shipped `03_architecture/realfield_architecture.md`의 "사람이 판단한 지점" 절로 대조합니다.

### Stage 3 · 플랜 (02_plan 비중첩 분할)
```
> 03_architecture 경계를 따라 02_plan/01_feature 에 todos를 만들고,
  모듈이 겹치지 않게 T1~T4 병렬 작업으로 나눠줘. common 공유 계약 소유자도 정해줘.
```
확인: T1~T4가 서로 다른 모듈만 만지는가, common 소유·합의 규칙이 정해졌는가.

---

## 16강 · Stage 4 : 병렬 구현과 검증 (멱등 랩)

> 16강은 15강에서 세운 plan을 코드로 내립니다. **여기서부터 lab.sh로 멱등하게 진행합니다.**

### 4-0. 시작 상태로 되돌립니다
```bash
./lab.sh reset
# 코드 7개 모듈(common·ingestion·transaction·analytics·discovery·config·gateway)의
# src/main/java 가 비워집니다.
# sdd 문서(00_sources)·테스트(스펙)·인프라 설정(application.yml)·게이트는 그대로입니다.
# 15강 산출물(01_planning·02_plan)이 없다면 먼저: ./lab.sh solve stage3
```

### 4-1. 네 에이전트로 비중첩 병렬 구현 (덱 16강의 병렬 호출과 동일)
모듈이 겹치지 않으므로 네 작업을 동시에 발화합니다.
```
>@ingestion-dev T1: data.go.kr 수집 + 정규화 + 회복력 + common 공유 계약 소유.
  WebClient 호출에 @Retry(3)·@CircuitBreaker(fallback=빈결과),
  Normalizer는 common/DealAmountParser로 콤마 금액 변환·해제(cdealType=O) 표시.
  공유 계약 common(AptTransaction·DealAmountParser)을 한곳에 둔다(T2·T3가 의존).

>@transaction-dev T2: 자연키 멱등 적재 + 조회.
  port/AptTradeStore + JPA 어댑터, existsByNaturalKey면 skip(AC-4).

>@analytics-dev T3: 시세 통계 read model.
  해제거래 제외 후 중위 거래금액·㎡당 단가 집계(AC-5·AC-3), transaction 조회.

>@platform-dev T4: 인프라 공통(디스커버리·설정·게이트웨이).
  Eureka(@EnableEurekaServer)·Config Server·API Gateway(8080 단일 진입점, 3 라우트).
```
결과는 `sdd/03_build/01_feature/realprice.md`에 current-state로 남깁니다(Overwrite Rule).

### 4-2. 게이트로 검증합니다 (봤다가 아니라 통과시켰다)
```bash
./lab.sh verify
# 1/2 아키텍처 게이트: 7개 모듈·common 역의존 없음·도메인→common 의존·
#                      게이트웨이 3라우트·analytics→transaction(CQRS)  → PASS (7/7)
# 2/2 gradle 단위 테스트: AC-3 금액/해제 · AC-4 멱등 · AC-5 중위 집계  → 8/8
```
라이브가 막히면 `./lab.sh solve`로 정답 구현을 복원해 같은 verify를 통과시킵니다.

> **멱등 보장:** `reset → 위 발화 → verify`를 몇 번 반복해도 아키텍처 게이트 PASS와 단위 8/8로 수렴합니다.
> 단위 테스트는 외부 data.go.kr를 호출하지 않는 순수 도메인 로직이라 네트워크·인증키 없이 결정적입니다.

### 4-3. (선택) 서비스 부팅 E2E
실제 게이트웨이·디스커버리·도메인 서비스를 함께 띄워 흐름을 확인하려면 contract의 deploy_dev를 씁니다.
게이트웨이로 `ingest → query → market-stats` 흐름을 스모크합니다(강사 환경, Docker 필요).

---

## 16강 (이어서) · 프론트엔드(web) : 발화로 3화면 + 브라우저 E2E

> 백엔드를 세웠으면 같은 plan/계약 위에 Next.js 프론트를 얹습니다. **백엔드와 동형**:
> 화면·공용 컴포넌트·api 구현만 비워 두고, 스캐폴딩(shadcn UI·계약 타입·게이트웨이 프록시·
> E2E 스펙)은 제공합니다. **실습은 `learning/web` 에서 합니다.**

주어지는 것(`learning/web` 스캐폴딩, 그대로 둠):
- `src/app/layout.tsx` · `src/components/site-nav.tsx` · `src/components/ui/*`(shadcn)
- `src/lib/types.ts`(백엔드 계약 1:1) · `src/lib/format.ts`(억/만원·㎡ 표기)
- `src/app/api/gateway/[...path]/route.ts`(게이트웨이 프록시, CORS 회피)
- `e2e/realfield.spec.ts`(결정적 브라우저 E2E) · `playwright.config.ts` · 빌드 설정

비워 둔 것(placeholder "TODO: 발화로 구현"):
- `src/app/{ingest,transactions,analytics}/page.tsx` · `src/app/page.tsx`(홈)
- `src/components/query-form.tsx`(거래·분석 공용 조회 폼)
- `src/lib/api.ts`(시그니처는 둠, 구현부 TODO)

### W-0. 시작 상태로 되돌립니다
```bash
cd learning
./lab.sh web-reset    # web 화면·컴포넌트·api 를 placeholder 로 (스캐폴딩은 보존)
./lab.sh web-build    # placeholder 상태에서도 타입에러 0으로 통과(빌드 게이트)
```
`./lab.sh reset` 을 쓰면 **백엔드 도메인 + web 을 한 발로** 함께 시작 상태로 되돌립니다.

### W-1. 세 화면을 발화로 구현
`lib/types`(계약)와 `lib/api` 시그니처를 입구로 화면을 채웁니다. placeholder 주석에
각 화면이 달아야 할 `data-testid` 가 명시되어 있습니다.
```
> ingest/page.tsx 구현: lawdCd(5자리)·dealYmd(YYYYMM) 입력 폼과 ingestAptTrade 호출,
  upserted 결과 카드(멱등: 재수집 0건). data-testid: ingest-lawdcd·ingest-dealymd·btn-ingest·ingest-result.

> transactions/page.tsx 구현: QueryForm(sggCd·년·월)으로 getTransactions 조회,
  동/단지 검색·면적 필터·해제거래 토글·정렬·페이징 테이블. data-testid: btn-search·transactions-table·tx-row·cancel-badge·filter-canceled.

> analytics/page.tsx 구현: getMarketStats + getTransactions 로 유효 거래건수·중위가·㎡당 단가 카드와
  면적-가격 산점도. data-testid: btn-analyze·stat-tradecount·stat-median·stat-perm2·price-chart.

> lib/api.ts 의 ingestAptTrade·getTransactions·getMarketStats 구현부를 프록시(/api/gateway/...) 호출로 채워줘.
```

### W-2. 브라우저 E2E 로 검증합니다
```bash
./lab.sh web-e2e
# 백엔드(docker 6서비스) + Next(:3000) 기동 후 Playwright 로:
#   수집(stub) → 거래조회(정상4+해제1=5행, 토글 시 4행) → 시세분석(tradeCount=4, median "8억…")
# 결정적(stub 프로필 고정값). HEADED=1 ./lab.sh web-e2e 로 브라우저 창을 띄워 시연할 수 있습니다.
```
라이브가 막히면 `./lab.sh web-solve`(또는 백엔드까지 함께 `./lab.sh solve`)로 정답 구현을
복원해 같은 E2E를 통과시킵니다. 완성본은 `complete/web` 에서 대조합니다.

> **멱등 보장:** `web-reset → 위 발화 → web-e2e`를 몇 번 반복해도 stub 고정값으로 같은 결과에
> 수렴합니다. placeholder 상태에서는 `web-build`(타입체크)는 통과, `web-e2e`는 실패가 정상입니다.

---

## 16강 마무리 · 본체 프레임워크 agentic-dev

이 부동산 레포는 **본체 프레임워크가 설치한 타깃**입니다. 데모로 SDD 흐름을 손으로 익혔다면,
대규모에서는 이 발화·분배·동기화를 자동화하는 본체가 필요합니다.
- 본체: `https://github.com/say828/agentic-dev` (설치기 + 멀티에이전트 오케스트레이터)
- 데모: `https://github.com/say828/agentic-dev-demo` (auth·finance·realestate 타깃)
- `sdd/02_plan`을 push하면 self-hosted runner 위 워크플로가 task IR → GitHub Project sync → 멀티에이전트 큐 → close로 자동 처리합니다.

> 한 문장: 명세와 아키텍처 판단이 서면, 데모 구현이든 대규모 자동화든 같은 plan을 입구로 씁니다.
