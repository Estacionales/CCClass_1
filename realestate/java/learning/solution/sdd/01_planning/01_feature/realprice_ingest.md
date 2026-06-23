# 실거래가 수집·집계 · Acceptance Criteria (EARS)

> 출처: 00_sources/realfield-부동산실거래 (원문 요구 1~5 → AC-1~AC-5)
> 각 AC는 통과/실패를 판정할 수 있는 검증 가능한 명세입니다. 구현 에이전트는 이 다섯 줄을 벗어날 수 없습니다.
> (1단계 '구조화' 산출물의 참조 정답입니다. HANDSON.md Stage 1에서 학습자가 직접 생성합니다.)

AC-1  When 특정 시군구(LAWD_CD)·계약월(DEAL_YMD)로 수집을 요청하면,
      the system shall data.go.kr 아파트 매매 실거래가 API를 호출해
      결과를 표준 스키마(AptTransaction)로 정규화하고 거래원장에 적재한다.

AC-2  When data.go.kr 응답이 지연되거나 실패하면,
      the system shall 재시도 3회 → 서킷브레이커 → 빈 결과(부분 수집)로
      우아하게 저하한다. 외부 장애가 파이프라인 전체를 멈추지 않는다. (회복력)

AC-3  The 거래금액 파싱은 shall 콤마·공백 포함 만원 문자열(" 82,500")을
      원 단위 정수(825,000,000)로 변환하고,
      해제된 거래(cdealType = O)는 시세 집계에서 제외한다. (데이터 정합)

AC-4  When 동일 (시군구·계약월) 수집이 재실행되면,
      the system shall 자연키 기반 멱등 upsert로 중복 거래를 만들지 않는다.

AC-5  When 시세 통계를 조회하면,
      the system shall 거래원장(write model)이 아니라 analytics read model에서
      중위 거래금액·중위 ㎡당 단가를 반환한다. (CQRS 읽기 분리)

AC-R  회귀: 게이트웨이 라우팅·디스커버리 등록·기존 조회 API 계약이 무손상이어야 한다.
