# 02_plan · 비중첩 작업 분할 (병렬 에이전트)

> 3단계 '플랜' 산출물입니다. 03_architecture의 경계를 따라 작업을 나눕니다.
> 비중첩이 핵심입니다. 모듈이 안 겹쳐야 네 에이전트를 동시에 돌려도 충돌이 없습니다.

```
[ ] T1 @ingestion-dev    data.go.kr 수집 + 정규화 + 회복력            (AC-1·AC-2·AC-3 변환)
[ ] T2 @transaction-dev  멱등 적재(자연키 upsert) + 조회 API           (AC-4)
[ ] T3 @analytics-dev    시세 통계 read model(중위가격·㎡단가)          (AC-5·AC-3 해제 제외)
[ ] T4 @platform-dev     디스커버리 + 게이트웨이 + Config 연계          (AC-R 라우팅)
```

## 비중첩 경계 (서로 다른 모듈만 만짐 → 병렬 안전)
```
T1 → ingestion-service/*       (MolitApiClient·Normalizer)
T2 → transaction-service/*     (포트/어댑터·멱등 커맨드·JPA)
T3 → analytics-service/*       (MarketStatCalculator·조회)
T4 → service-discovery/* · config-server/* · api-gateway/*
```

## cross-cutting (공유 계약)
- `common/AptTransaction`·`common/DealAmountParser`는 T1·T2·T3가 모두 의존합니다.
  공유 계약으로 빼서 **T1이 소유**하고, 변경 시 세 에이전트가 합의합니다.
  금액 파싱(AC-3)을 common에 두면 어느 모듈에서 적재·집계해도 같은 규칙을 강제할 수 있습니다.
