# 03_build · 도서·회원·대출 3모듈 strangler 전환 구현 요약

## 구현 범위

`sdd/01_planning/01_feature/{book,member,loan}.md` 스펙에 따라 서브에이전트 3개를 병렬 실행해
`kr.elice.library.springboot` 패키지에 신규 구현 3종을 각각 독립된 파일로 신규 작성했다.

- `src/main/java/kr/elice/library/springboot/NewBookService.java`
  - `BookService` 구현. 공유 `BookStore` 사용. 빈 이름 `newBookService`(스프링 기본 규약).
  - `get()` 미존재 시 `LibraryException.Code.NOT_FOUND`.
- `src/main/java/kr/elice/library/springboot/NewMemberService.java`
  - `MemberService` 구현. 공유 `MemberStore` 사용. 빈 이름 `newMemberService`.
  - `get()` 미존재 시 `LibraryException.Code.NOT_FOUND`.
- `src/main/java/kr/elice/library/springboot/NewLoanService.java`
  - `LoanService` 구현. 공유 `LoanStore` 사용. 빈 이름 `newLoanService`.
  - **도서·회원 조회는 `platform.CatalogRouter` 로만 접근** (`router.books().get(bookId)`,
    `router.members().get(memberId)`). Legacy/New 어느 조합이든 활성 구현을 그대로 따라간다.
  - AC-1(활성 대출 5건 한도), AC-2(연체 보유 시 신규 대출 거부) 규칙을 레거시와 동일하게 구현.

## 전환 상태 변경

`src/main/resources/migration.properties` 세 모듈을 전부 `legacy` → `new` 로 전환:

```
module.books=new
module.members=new
module.loans=new
```

## 변경하지 않은 것

라우터(`CatalogRouter`/`LoanRouter`/`Routing`), 컨트롤러, 예외 처리, 저장소, 레거시 구현,
도메인 모델은 스펙대로 기존 그대로 두고 손대지 않았다.

## 실행 방식 메모

세 모듈은 서로 다른 파일 하나씩만 만들면 되는 독립 작업이라 서브에이전트 3개를 한 메시지에서
동시에 기동해 병렬로 구현시켰다. 각 서브에이전트에게 gradle 빌드/테스트 실행은 금지시키고
(동시 gradle 데몬 충돌 방지), 파일 작성만 맡긴 뒤 오케스트레이터가 통합 후 1회씩
컴파일·테스트를 수행했다.
