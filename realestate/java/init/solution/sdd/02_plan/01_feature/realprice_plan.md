# 02_plan · 작업 계획

> 3단계 '플랜' 산출물입니다. 모듈 의존·런타임 흐름·proof 게이트를 확정합니다.

## 모듈 의존 그래프
```
common ──┬─→ ingestion-service ──(WebClient)──→ transaction-service
         ├─→ transaction-service
         └─→ analytics-service ──(WebClient, lb)──→ transaction-service

service-discovery(Eureka) ← 모든 서비스 등록
config-server ← ingestion 설정·인증키 외부화
api-gateway ← 단일 진입점 (ingest·transactions·market-stats 라우팅)
```

## 런타임 흐름 (한 기능 end-to-end)
```
POST /api/v1/ingest/apt-trade?lawdCd=11110&dealYmd=202405
  → api-gateway → ingestion-service
      → MolitApiClient.fetchAptTrades  (data.go.kr, 재시도·서킷)
      → AptTransactionNormalizer       (금액 변환·해제 표시)
      → POST lb://transaction-service /api/v1/transactions/bulk  (멱등 upsert)

GET /api/v1/market-stats?sggCd=11110&dealYear=2024&dealMonth=5
  → api-gateway → analytics-service
      → GET lb://transaction-service /api/v1/transactions
      → MarketStatCalculator           (해제 제외·중위 집계)
```

## proof 게이트 (02_plan acceptance)
- AC-1·AC-3: `AptTransactionNormalizerTest`
- AC-3: `DealAmountParserTest`
- AC-4: `IdempotentUpsertTest`
- AC-5·AC-3: `MarketStatCalculatorTest`
- 전체: `./gradlew test` exit 0 (강사 환경 JDK 21 + Gradle)
