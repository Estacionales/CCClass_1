# T4 · 플랫폼(service-discovery·config-server·api-gateway) · 작업 계획

> SDD 'plan' 산출물. 대상 위치: `sdd/02_plan/01_feature/05_t4_platform.md`
> 소유 에이전트: `platform-dev`. 건드리는 모듈: `service-discovery/**`, `config-server/**`,
> `api-gateway/**`만. `common/**`은 건드리지 않는다(T4는 D-4상 common에 의존하지 않음).

## Scope
- 변경 대상 모듈: `service-discovery/**`, `config-server/**`, `api-gateway/**`.
- 범위 밖: 도메인 서비스(T1/T2/T3) 내부 구현. T4는 세 서비스의 존재와 라우팅/등록/설정 공급만 책임진다.

## Assumptions
- 환경: DEV(개발계)
- 의존/선결 조건: 없음. `common`에 의존하지 않으므로 Phase 0을 기다리지 않고 즉시 시작 가능
  (`00_overview.md` 시퀀싱). 단, 게이트웨이 라우트·컨트랙트 값은 `05_api/realprice_api.md`가 이미
  확정되어 있어 그 스펙을 그대로 반영하면 된다(T1/T2/T3 구현 완료를 기다릴 필요 없음).

## Acceptance Criteria
- SIR-003: 게이트웨이가 `/api/v1/ingest/**`, `/api/v1/transactions/**`, `/api/v1/market-stats/**`
  3개 라우트를 단일 진입점으로 노출한다(이미 `api-gateway/application.yml`에 존재 — 유지·검증만).
- SIR-004: 도메인 서비스가 Eureka(`service-discovery`)에 등록되어 `lb://` 로드밸런싱이 동작한다.
- SECR-001/002: 인증키·엔드포인트·회복력 정책이 `config-server`로 외부화되고 평문 비밀값이 없다.
- 배포 순서(`99_toolchain/02_policies/deployment_order.md`): discovery → config-server → gateway →
  도메인 서비스 순으로 기동해도 정상 등록된다.

## 모듈 의존 그래프
```
service-discovery (Eureka, 등록 대상 없음)
config-server (native profile, classpath:/config)
api-gateway ──(discovery locator + 명시 라우트 3개)──→ ingestion-service / transaction-service / analytics-service
```
(T4 세 모듈은 서로 및 도메인 서비스에 컴파일타임 의존이 없다 — 런타임 등록/설정 공급 관계만 있다.)

## 런타임 흐름 (end-to-end)
```
기동: service-discovery(8761) → config-server(8888) → api-gateway(8080) → 도메인 서비스(8081-8083)
요청: 외부 클라이언트 → api-gateway → (Eureka lb://) → 도메인 서비스
```

## 회귀 범위 (regression scope)
- 직접: `service-discovery/**`, `config-server/**`, `api-gateway/**`.
- 상류: 없음(플랫폼이 최상단 진입점).
- 하류: T1/T2/T3 세 도메인 서비스의 Eureka 등록·라우팅 대상 여부(존재 확인만, 내부 구현은 각 트랙 책임).
- 공유: `config-server`가 배포하는 `molit.*`, `resilience4j.*` 설정값 — T1(ingestion-dev)과 값 정합을
  맞춰야 하는 공유 지점(§공유 파일 경계).
- 정당화된 제외: 도메인 서비스 내부 로직(각 트랙 회귀 범위).

## 공유 파일 경계 (T1과의 조율 필요)

- `config-server/src/main/resources/config/ingestion-service.yml`의 `molit.apt-trade-path`는
  T4가 소유·수정하되, 값은 `01_planning/07_integration/molit_integration.md` §1이 확정한
  `/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev`로 정정한다. T1이 소유한
  `ingestion-service/application.yml`의 로컬 기본값과 최종적으로 같은 값이어야 하며, 값 불일치가
  생기면 T1에 통지한다(직접 T1의 파일을 수정하지 않는다).

## Execution Checklist
- [x] 세 인프라 모듈 부트스트랩 클래스 신규 작성: `DiscoveryApplication`(@EnableEurekaServer),
      `ConfigServerApplication`(@EnableConfigServer), `ApiGatewayApplication`(plain @SpringBootApplication).
      레퍼런스 솔루션과 패키지·클래스명·애너테이션 동일(각 ~12줄, main만)
- [x] `config-server/src/main/resources/config/ingestion-service.yml`의 `molit.apt-trade-path`를
      상세(Dev) 엔드포인트로 정정(§공유 파일 경계). T1은 자기 소유 `ingestion-service/application.yml`
      복사본을 이미 동일 값으로 정정 완료(`02_t1_ingestion.md` §드리프트 정정) — 두 복사본 값 일치
- [x] 게이트웨이 3개 라우트(`/api/v1/ingest/**`, `/api/v1/transactions/**`, `/api/v1/market-stats/**`)
      존재 확인 — 이미 정의되어 있으므로 변경 없이 확인만
- [x] `POST /internal/transactions/batch-upsert`(`05_api` §3b)가 게이트웨이 라우트에 노출되지
      않았는지 확인(서비스 간 전용 경로, 외부 노출 금지) — 게이트웨이 yml에 미노출 확인
- [ ] service-discovery 기동 후 도메인 서비스 3종 등록 확인(수동 또는 통합 테스트) — 런타임 검증,
      T2/T3 메인 소스 완성·기동 후 오케스트레이션 세션에서 확인 대상(본 턴 미수행)
- [x] `MOLIT_SERVICE_KEY` 등 비밀값이 config 파일에 평문으로 없는지 확인(SECR-001, `09_security` §3.1)
      — `service-key: ${MOLIT_SERVICE_KEY:}` 환경변수 참조만, 평문 비밀값 없음
- [ ] 배포 순서 정책(discovery → config-server → gateway → 도메인) 기동 스크립트/문서 반영 —
      기동 스크립트 작성은 본 턴 범위 밖(정책 정본은 `99_toolchain/02_policies/deployment_order.md`)

## Current Notes
- 2026-07-02: 계획 수립.
- 2026-07-02: T4 구현 완료(부트스트랩 3종 + config-server 엔드포인트 드리프트 정정). 빌드·구조 게이트
  최종 검증은 오케스트레이션 세션이 독립 수행(본 트랙 미실행). current-state는
  `sdd/03_build/01_feature/05_t4_platform.md`.

## Validation (proof 게이트)
- `python3 sdd/99_toolchain/01_automation/run_arch_check.py` exit 0 (규칙 1 "필수 7개 모듈", 규칙 4 "게이트웨이 3개 라우트")
- 수동/통합: discovery 콘솔(`http://localhost:8761`)에서 3개 도메인 서비스 등록 확인
