# Integration: data.go.kr(MOLIT) 아파트 매매 실거래가 연계 계약 (molit_integration)

> SDD 1단계(01_planning) 정본. `00_sources/01_apis/molit_apt_trade_api.md`(외부 공개 명세)를
> 시스템 측 연계 계약(엔드포인트 선택, 회복력 정책 값, 동시성·스케줄링 규칙, 에러 처리 매트릭스)으로
> 구체화한다. 08_nonfunctional(NFR-REL-*)과 09_security(SEC-001~003)가 참조하는 정본이 본 문서다.

---

## 1. 엔드포인트 결정

| 항목 | 값 | 근거 |
| --- | --- | --- |
| 채택 엔드포인트 | `getRTMSDataSvcAptTradeDev` (상세) | 2024년 확장 항목(해제여부·등기일자·거래유형·매도자매수자구분 등)을 모두 포함해야 AC-3(해제 제외)·SFR-012(등기·거래유형 보존)를 만족할 수 있다. |
| URL | `https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev` | HTTPS 권장(원문 §2) |
| 기각한 대안 | 기본 엔드포인트 `getRTMSDataSvcAptTrade` | 해제여부(`cdealType`) 등 신규 항목이 없어 AC-3를 구조적으로 만족할 수 없음. 요구사항정의서 §2.4 부록 A가 이미 상세 엔드포인트를 표준으로 명시. |

- **드리프트 정정 지시**: `config-server/src/main/resources/config/ingestion-service.yml`의
  `molit.apt-trade-path`가 현재 기본 엔드포인트(`/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade`)를 가리킨다.
  본 계약 확정에 따라 구현 시 `/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev`로 정정한다
  (이미 `01_feature/realprice_ingest.md` §5에 드리프트로 기록됨. 본 문서가 정정 값의 정본).

## 2. 요청 계약

| 파라미터 | 값 | 비고 |
| --- | --- | --- |
| `serviceKey` | 환경변수 `MOLIT_SERVICE_KEY` 참조(Decoding 키) | SECR-001. 평문 저장 금지 |
| `LAWD_CD` | 시군구 5자리 | DAR-008 마스터 참조 |
| `DEAL_YMD` | `YYYYMM` | AC-1 |
| `pageNo` | 1부터 순증 | SFR-002 |
| `numOfRows` | `1000`(고정) | PER-002. 페이징 호출 수 최소화 |

## 3. 응답 처리 계약 (에러 코드 매트릭스)

> 원문 코드 정의는 `00_sources/01_apis/molit_apt_trade_api.md` §6. 아래는 수집 서비스(`ingestion-service`)가
> 실제로 취해야 할 처리를 확정한 시스템 계약이다.

| resultCode | 의미 | 시스템 처리 | 재시도 대상 | 근거 |
| --- | --- | --- | --- | --- |
| `000` | 정상 | item 정규화(AC-1, AC-3)·적재 | - | SFR-001 |
| `01` | APPLICATION ERROR | §4 재시도 정책 적용 | Y | SIR-005 |
| `03` | NODATA ERROR | 정상 종료(빈 결과), 적재 없음, 실패로 집계하지 않음 | N | SFR-002 |
| `04` | HTTP ERROR | §4 재시도 정책 적용 | Y | SIR-005 |
| `12` | NO OPENAPI SERVICE ERROR | 즉시 실패, 해당 `sggCd`+`dealYm` job을 `FAILED`로 기록, 운영 알림 | N | SFR-011(부분 수집 유지) |
| `20` | SERVICE ACCESS DENIED | 즉시 실패, 운영 알림(키 권한 점검) | N | SECR-001 |
| `22` | 트래픽 한도 초과 | §5 백오프·이월 정책 적용 | 조건부(익일) | CONR-001 |
| `30` | SERVICE KEY IS NOT REGISTERED | 즉시 실패, 운영 알림(키 점검) | N | SECR-005 |
| `31` | DEADLINE HAS EXPIRED | 즉시 실패, 운영 알림(키 갱신) | N | SECR-005 |
| `32` | UNREGISTERED IP ERROR | 즉시 실패, 운영 알림(IP 등록) | N | - |
| `99` | UNKNOWN ERROR | §4 재시도 정책 적용 | Y | SIR-005 |
| HTTP 타임아웃/네트워크 오류 | - | §4 재시도 정책 적용 | Y | SIR-005 |

- "즉시 실패"는 해당 `sggCd`+`dealYm` 단위 job만 실패 처리하며, 배치 전체(다른 시군구·연월)는 계속
  진행한다(SFR-011, `05_api/realprice_api.md` §2 `partial: true`).

## 4. 재시도·서킷브레이커 정책 값 (resilience4j)

> 본 절이 정책 값의 정본이다. `08_nonfunctional/realprice_nonfunctional.md` NFR-REL-001/002는 본 절을 참조한다.
> 현재 `config-server/src/main/resources/config/ingestion-service.yml`에 반영된 값과 동일하며, 값 변경 시
> 이 문서를 먼저 갱신한다.

```yaml
resilience4j:
  circuitbreaker:
    instances:
      molitApi:
        sliding-window-size: 20        # 최근 20회 호출 기준 실패율 산정
        failure-rate-threshold: 50     # 실패율 50% 이상이면 서킷 오픈
        wait-duration-in-open-state: 10s
  retry:
    instances:
      molitApi:
        max-attempts: 3
        wait-duration: 500ms
```

- 적용 대상: resultCode `01`/`04`/`99` 및 HTTP 타임아웃·네트워크 오류(§3).
- 서킷 오픈 중 요청은 즉시 실패 처리하고 해당 페이지를 스킵(부분 수집)한다. half-open 전환 후 정상 호출이
  성공하면 서킷을 닫는다(resilience4j 기본 동작).

## 5. 트래픽 한도·동시성·스케줄링 계약

| 항목 | 값 | 근거 |
| --- | --- | --- |
| 개발계정 일일 한도 | 10,000건 | CONR-001 |
| 동시 수집 제한 | 시군구 단위 최대 5개 동시 실행(세마포어) | PER-004("제한적 동시 실행"의 구체값). 250개 시군구 × 1회 호출(1000건 페이지 가정 시 평균 1~2페이지)로도 한도 내 완료 가능하도록 보수적으로 설정 |
| 트래픽 초과(22) 시 백오프 | 지수 백오프(최초 1분, 최대 3회) 후에도 실패하면 해당 job을 익일 자동 재개 큐에 적재 | CONR-001, SFR-011 |
| 정기 수집 주기 | 매월 1회, (시군구 × 계약월) 전체 조합 배치 | SFR-010 |
| 수동 트리거 | `POST /api/v1/ingest/jobs`(단건 `sggCd`+`dealYm`) | SFR-010, `05_api/realprice_api.md` §2 |
| 백필(재수집) | 과거 계약월 구간에 동일 엔드포인트·동일 동시성 제한 적용 | SFR-013, AC-4 |

- **기각한 대안**: "동시성 제한 없이 250개 시군구를 병렬 수집". 일일 한도(10,000건)를 손쉽게 초과할 위험이
  있고(PER-004 위반), 트래픽 초과(22) 발생 시 익일 이월이 반복되면 오히려 전체 배치 완료가 늦어진다. 기각.
- **기각한 대안**: "고정 지연(sleep) 없이 순차 호출만 사용". 250개 시군구 순차 처리 시 배치 완료 시간이
  과도하게 길어져 PER-002(처리량 목표)를 만족하기 어렵다. 제한적 동시성(5)으로 처리량과 한도 준수를 함께
  만족시키는 현재안을 채택.

## 6. 요구사항 추적표

| 계약 절 | 관련 SIR/PER/CONR | 관련 AC |
| --- | --- | --- |
| 엔드포인트 결정(§1) | SIR-001 | AC-1, AC-3 |
| 요청 계약(§2) | SFR-002, DAR-008, SECR-001 | AC-1 |
| 에러 코드 매트릭스(§3) | SIR-005, SFR-011 | AC-2 |
| 재시도·서킷(§4) | SIR-005 | AC-2 |
| 트래픽·동시성·스케줄링(§5) | PER-004, CONR-001, SFR-010, SFR-013 | AC-2, AC-4 |

## 7. 범위 밖

- 인증키 마스킹 로깅 구현 세부는 `09_security/realprice_security.md` §3.2를 정본으로 한다(본 문서는 계약값만 다룸).
- 스케줄러 오케스트레이션(cron 트리거 구현체, 잡 큐 저장소)은 `01_planning/06_iac`(후속 작성 대상)에서 다룬다.
