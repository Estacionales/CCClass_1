# realestate — 부동산 대규모 MSA 데모 (init / learning / complete)

15·16강 "부동산 대규모 프로젝트" 실습의 러닝 예제입니다. 실재 공개 데이터
(data.go.kr 국토교통부 실거래가)를 소재로, Java 17 · Spring Boot · Spring Cloud 로
만든 마이크로서비스(MSA)를 SDD 5단계로 세웁니다. 도메인 모듈
(common · ingestion-service · transaction-service · analytics-service)과 인프라 모듈
(service-discovery · config-server · api-gateway)로 나뉩니다. 같은 예제를 두 형태로 둡니다.

| 폴더 | 버전 | 무엇인가 |
| --- | --- | --- |
| `learning/` | 실습 버전 | 강의 시작 상태. `sdd/00_sources`(발주 3벌) + 테스트 스펙 + 아키텍처 게이트 + 인프라 설정(application.yml)만 있고, 코드 7개 모듈의 `src/main/java` 와 15강 산출물(`01_planning`·`02_plan`)은 비어 있습니다. **학습자가 발화로 채웁니다.** |
| `init/` | 시작 보관본 | `learning/` 과 같은 시작 상태를 손대지 않고 보존합니다. 실습이 꼬이면 여기서 다시 시작합니다. |
| `complete/` | 완성 버전 | 코드 7개 모듈 + 15강 산출물이 모두 채워진 완성본. 아키텍처 게이트 7/7 PASS + gradle 단위 8/8 통과. 정답·대조용. |

## 실습 방법

1. `cd learning` 에서 시작합니다. PPT(15·16강)와 `HANDSON.md`의 발화 흐름을 따라
   Claude Code 로 코드 모듈을 구현합니다(T1~T4 역할 에이전트: ingestion·transaction·analytics·platform-dev).
   - 15강: 요구사항 정제와 아키텍처 판단(Stage 1~3). `sdd/00_sources` 하나에서
     `01_planning` → `02_plan` 을 발화로 생성합니다(시작 상태에는 비어 있음).
   - 16강: 비중첩 플랜을 병렬로 코드에 내리고(Stage 4) 게이트·테스트로 검증합니다.
     16강만 새로 시작하면 `./lab.sh solve stage3` 로 15강 산출물(가드레일)을 먼저 깝니다.
2. 막히거나 결과를 대조하려면 `complete/` 를 보거나 `./lab.sh solve`(코드)·`solve stage3`(산출물)로 복원합니다.

## 각 버전 검증 (동일 명령)

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
./lab.sh status     # 도메인 구현 존재 여부
./lab.sh verify     # 아키텍처 게이트(7) + gradle 단위 테스트(8)
./lab.sh e2e        # 6개 서비스 docker compose 부팅 + 게이트웨이 통과 E2E (Docker 필요)
```

- `complete/` : 아키텍처 게이트 7/7 PASS · 단위 8/8 통과.
- `learning/`·`init/` : 시작 시 코드 구현이 없어 컴파일에서 멈춥니다. 코드 7개 모듈을 채우면
  complete 와 같은 결과로 수렴합니다(또는 `./lab.sh solve`).

## 프론트엔드 (web) — Next.js + 브라우저 E2E

각 버전에는 백엔드 게이트웨이(8080)에 붙는 Next.js 15 프론트(`web/`)가 함께 있습니다.
3화면(`/ingest` 수집 · `/transactions` 거래조회 · `/analytics` 시세분석)을 Next route
handler 프록시(`/api/gateway/...`)로 게이트웨이에 연결합니다. **백엔드와 동형**으로
구현부만 비우고 스캐폴딩은 제공합니다.

| 버전 | web 상태 |
| --- | --- |
| `init/web`, `learning/web` | 시작 상태(placeholder). 화면·공용 컴포넌트(query-form)·`lib/api` 구현이 비어 있고 "TODO: 발화로 구현" 스텁만 있습니다. 스캐폴딩은 제공됩니다: `layout`·`site-nav`·`ui/*`(shadcn)·`lib/types`·`lib/format`·프록시 route handler·E2E 스펙·설정. **학습자가 `learning/web`에서 발화로 채웁니다.** |
| `complete/web` | 3화면이 모두 구현된 완성본. 빌드·브라우저 E2E 통과. 정답·대조용. |

프론트 발화 흐름: `lib/types`(백엔드 계약 1:1)와 `lib/api` 시그니처를 입구로,
각 화면을 발화로 구현합니다 — 수집 폼→`ingestAptTrade`(멱등 upserted), 거래조회→
`getTransactions`(검색·필터·정렬·페이징), 시세분석→`getMarketStats`+산점도.
E2E가 기대하는 `data-testid`(`btn-ingest`·`transactions-table`·`stat-median` 등)는
placeholder 주석에 명시되어 있습니다.

```bash
# (web 명령은 Node.js 필요. 백엔드 명령과 한 lab.sh 안에 있습니다.)
./lab.sh status        # 백엔드 + web 구현 상태(placeholder/구현됨)를 함께 표시
./lab.sh web-build     # next build — placeholder 상태에서도 타입에러 0으로 통과
./lab.sh web-dev       # 개발 서버(:3000) — 강의 시연용
./lab.sh web-e2e       # 백엔드(docker 6서비스) + Next(:3000) + Playwright 브라우저 E2E
./lab.sh web-reset     # web 화면·컴포넌트·api 구현만 placeholder 로 되돌림(스캐폴딩 보존)
./lab.sh web-solve     # web/solution → web/src 정답 복원(라이브 폴백)
```

- `learning/web`, `init/web` : placeholder 상태로 `web-build`는 통과(타입에러 0)하지만,
  실제 화면 동작이 없어 `web-e2e`는 실패하는 것이 정상입니다. 발화로 채우면 통과합니다.
- `complete/web` : `web-build` · `web-e2e` 모두 통과.
- `./lab.sh reset` / `./lab.sh solve` 는 **백엔드 도메인 + web 을 한 발로** 함께
  처리합니다(web-* 단독 명령도 유지). complete/web 에는 placeholder/solution 스냅샷이
  없어 reset/solve 가 web 을 건드리지 않습니다(정답 보존).

## 멱등성

단위 테스트는 난수·실시간·네트워크에 의존하지 않습니다. 외부 data.go.kr 호출은
런타임 전용이고 단위 검증은 순수 도메인 로직만 봅니다. 적재는 거래 자연키로 멱등
처리되어 같은 입력을 여러 번 넣어도 한 번만 반영됩니다. 학습자의 구현 코드가 매번
조금씩 달라도, 고정된 아키텍처 게이트와 테스트 스펙을 통과하는 한 항상 같은 결과로
수렴합니다.
