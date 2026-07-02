# 02_plan · 도서·회원·대출 3모듈 strangler 전환 (신규 구현 + all-new 전환)

## Scope

- `sdd/01_planning/01_feature/{book,member,loan}.md` 스펙에 따라 `kr.elice.library.springboot` 패키지에
  `NewBookService` · `NewMemberService` · `NewLoanService` 세 클래스를 신규 작성한다.
- 세 모듈을 서브에이전트 3개로 병렬 배정해 동시에 구현한다 (모듈당 파일 1개, 파일 충돌 없음).
- `NewLoanService` 는 도서·회원 활성 구현을 직접 참조하지 않고 `platform.CatalogRouter` 로 받아 호출한다.
- 세 파일 구현이 모두 끝나면 `src/main/resources/migration.properties` 의
  `module.books` · `module.members` · `module.loans` 를 모두 `new` 로 전환한다.

## Assumptions

- 저장소(`BookStore`/`MemberStore`/`LoanStore`), 인터페이스(`api/*Service`), 라우터
  (`CatalogRouter`/`LoanRouter`/`Routing`), 컨트롤러, 예외 처리는 이미 구현되어 있고 변경하지 않는다.
- 빈 이름은 스프링 기본 규약(클래스명 첫 글자 소문자)을 따른다: `newBookService` / `newMemberService` /
  `newLoanService`. 라우터가 이 이름으로 빈을 찾는다.
- 대출 한도(AC-1, 5권)·연체 거부(AC-2) 규칙은 신규 구현에서도 레거시와 동일하게 지켜야 한다.
- 단일 애플리케이션 컨텍스트 안에 legacy·new 구현이 공존하므로, 세 서브에이전트는 서로 다른 파일만
  건드려 병렬 작업 중 충돌이 없다.

## Acceptance Criteria

- AC-B1/B2/B3, AC-M1/M2, AC-L1/AC-1/AC-2/AC-L2 (스펙 표 그대로) 가 `new` 구현으로도 성립한다.
- `AllNewModeTest.allNewBeansRegistered` : `newBookService`/`newMemberService`/`newLoanService` 빈이
  모두 컨텍스트에 등록된다.
- `AllNewModeTest.newLoanUsesCatalogRouter` 등 all-new 테스트 전부 GREEN.
- `LibraryAcceptanceTest` (모드 무관 채점기) 가 `migration.properties` all-new 전환 후에도 GREEN.
- `run_strangler_check.py` 실행 시 3/3 전환 완료로 보고되고 불일치 없음.

## Execution Checklist

- [x] 계획 수립 (본 문서)
- [x] 서브에이전트 3개 병렬 실행: `NewBookService` / `NewMemberService` / `NewLoanService` 구현
- [x] 컴파일 및 전체 테스트 1회 실행 (legacy 기본 모드 상태에서 회귀 없음 확인)
- [x] `migration.properties` 세 모듈 모두 `new` 로 전환
- [x] all-new 상태에서 `./gradlew test` 재실행 및 `run_strangler_check.py` 실행
- [x] `sdd/03_build/01_feature`, `sdd/04_verify/01_feature` 기록

## Notes

- 배포/운영(`05_operate`) 대상 아님: 이 저장소는 인메모리 학습용 데모이며 별도 DEV/PROD 환경이 없다.
  롤아웃 요청이 없으므로 `05_operate` 갱신은 생략한다.
- 영속성/스키마 변경 없음 (인메모리 `ConcurrentHashMap` 저장소 그대로 재사용).

## Validation

- `./gradlew test` (legacy 기본값, all-new 전환 후 각 1회) 결과를 `sdd/04_verify/01_feature` 에 기록.
- `python sdd/99_toolchain/01_automation/run_strangler_check.py` 결과를 함께 기록.
