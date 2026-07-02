# common · 공유 계약 (Phase 0) · 작업 계획

> SDD 'plan' 산출물. 대상 위치: `sdd/02_plan/01_feature/01_common_contract.md`
> 소유 에이전트: `backend-dev`. **`common/**`의 유일한 쓰기 담당자** — T1~T4는 이 모듈을 소비만 한다
> (`00_overview.md` 모듈 비중첩 원칙).

## Scope
- 변경 대상 모듈: `common/**` (java-library, 부트 실행 대상 아님).
- 산출물: `AptTransactionDto`, `DealAmountNormalizer`, `CancelStatusResolver`, `MolitDateParser`,
  `AptTransactionNaturalKey`. 필드·규칙 정의는 `01_planning/04_data/realprice_data.md` §1.1, §1.2, §4가 정본.
- 범위 밖: LAWD_CD 마스터 데이터 적재(§3, 필요 시 별도 후속 plan 항목).

## Assumptions
- 환경: DEV(개발계)
- 의존/선결 조건: 없음(common은 도메인 모듈에 의존하지 않음, D-4). 이 트랙이 Phase 0으로 T1/T2/T3보다
  먼저(또는 최소 인터페이스 프리즈 시점까지) 완료되어야 한다.

## Acceptance Criteria
- AC-1(부분): `AptTransactionDto`가 `04_data` §1.1 필드 전체를 손실 없이 표현한다.
- AC-3(부분): `DealAmountNormalizer`가 `"  82,500"` → `825000000`(long)으로 변환하고, 파싱 불가·0 이하
  결과는 예외 또는 `Optional.empty()`로 스킵 신호를 준다(품질 게이트, 데이터명세서 §5).
- AC-3(부분): `CancelStatusResolver`가 `cdealType == "O"` → `true`, 공백 → `false`를 반환한다.
- AC-4(부분): `AptTransactionNaturalKey`가 `04_data` §1.2의 9개 필드로 `equals`/`hashCode`를 구현해
  재수집 시 동일 거래를 동일 키로 판정한다.
- 구조 게이트: `common` 소스에 `kr.elice.realfield.ingestion|transaction|analytics` import가 없다
  (`run_arch_check.py` 규칙 2).

## 모듈 의존 그래프
```
common (java-library, 역의존 없음)
  ↑ implementation project(':common')
  ├── ingestion-service
  ├── transaction-service
  └── analytics-service
```

## 런타임 흐름 (end-to-end)
```
(런타임 아님 — common은 컴파일타임 라이브러리. 각 도메인 서비스가 자기 프로세스 안에서
 common의 클래스를 직접 호출한다. 네트워크 홉 없음.)
```

## 회귀 범위 (regression scope)
- 직접: `common/**`.
- 상류: 없음(common을 호출하는 상위 서비스가 없음, common이 최하단 의존).
- 하류: `ingestion-service`, `transaction-service`, `analytics-service` 전체 — 이 셋의 컴파일이
  `common`의 공개 API 시그니처에 의존한다. `common`의 시그니처를 바꾸면 하류 3개 모듈을 모두 재확인한다.
- 공유: 그 자체가 공유 계약.
- 정당화된 제외: 없음. 하류 3개 모듈의 컴파일 확인까지가 이 트랙의 회귀 범위다.

## Execution Checklist
- [ ] `AptTransactionDto` 정의 (`04_data` §1.1 필드 전체, `kr.elice.realfield.common.dto`)
- [ ] `DealAmountNormalizer` 구현 + 단위테스트(경계값: 선행 공백, 콤마, 0, 음수, 파싱 불가 문자열)
- [ ] `CancelStatusResolver` 구현 + 단위테스트(`O`, 공백, null)
- [ ] `MolitDateParser` 구현 + 단위테스트(`YY.MM.DD` → `LocalDate`, 공백 → null, 세기 결정 규칙 명시)
- [ ] `AptTransactionNaturalKey` 값 객체 구현(9개 필드 `equals`/`hashCode`) + 단위테스트(동일 키 재계산 시 동등성)
- [ ] `run_arch_check.py` 규칙 2(common 역의존 없음) 로컬 확인
- [ ] 공개 API 확정 공지 — T1/T2/T3 트랙에 "소비 가능" 신호(Phase 1 시작 조건)

## Current Notes
- 2026-07-02: 계획 수립. 구현 착수 전.

## Validation (proof 게이트)
- `./gradlew :common:test` exit 0
- `python3 sdd/99_toolchain/01_automation/run_arch_check.py` exit 0 (규칙 2 "common이 도메인 모듈에 역의존하지 않음")
