# 01_planning INDEX: RealField

> 00_sources 요구사항을 구조화한 계획 산출물의 색인입니다.
> 외부 API 명세 원천: `00_sources/01_apis/molit_apt_trade_api.md`(data.go.kr 아파트 매매 실거래가). 요구사항정의서: `00_sources/02_requirements/realfield-부동산실거래.md`.

| 섹션 | 파일 | 내용 |
| --- | --- | --- |
| 01_feature | `01_feature/realprice_ingest.md` | 기능 수용기준 (EARS AC-1~AC-5) |
| 03_architecture | `03_architecture/realfield_architecture.md` | MSA 경계·런타임·**사람의 아키텍처 판단** |
| 04_data | `04_data/realprice_data.md` | 표준 거래 스키마·자연키·정합 규칙 |
| 05_api | `05_api/realprice_api.md` | 게이트웨이 라우팅·엔드포인트 계약 |
| 07_integration | `07_integration/molit_integration.md` | data.go.kr 연계 계약·회복력 |
| 08_nonfunctional | `08_nonfunctional/realprice_nfr.md` | 성능·회복력·멱등·가용성 |
| 09_security | `09_security/realprice_security.md` | 인증키 비노출·감사 |

> 진행 순서는 `HANDSON.md`를 따릅니다. 기능·비기능·보안(Stage 1) → 아키텍처·데이터·API·연계(Stage 2) → 플랜(Stage 3).
