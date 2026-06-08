# library · 레거시 strangler 전환 데모 (13강)

13강 "레거시를 한 모듈씩 Spring Boot 로 전환합니다" 실습 타깃입니다. 도서관(도서·회원·대출)
레거시를 앞단 라우터를 두고 모듈 하나씩 신규 구현으로 옮기는 strangler 패턴을 직접 실습합니다.

> Java 17 · Spring Boot 3.5 · Gradle. 외부 DB 없이 인메모리로 동작합니다.

## 한눈에 보기

- `legacy/` 패키지: 도서·회원·대출의 **시작 코드**(제공). 학습자는 이 코드를 스펙으로 풉니다.
- `springboot/` 패키지: **학습자가 채우는 신규 구현**(시작 시 비어 있음).
- `platform/`: 앞단 라우터와 컨트롤러. `migration.properties` 에 따라 모듈별로 legacy|new 분기.
- `store/`: 공유 인메모리 저장소(실제 전환에서의 공유 DB 역할). legacy·new 가 같은 데이터를 봅니다.
- `src/test/`: 수용기준(AC-1 대출 한도 5권 · AC-2 연체 거부). 전환 전·후 모두 통과해야 하는 **고정 채점기**.

## 발화만으로 실습 (PPT 13강 싱크)

학습자는 `PROMPTS.md` 의 세 발화를 Claude Code 에 순서대로 말하면 됩니다. 손으로 코드를
짤 필요가 없습니다. 도서 → 회원 → 대출 순으로 한 모듈씩 전환됩니다.

## 클론-앤-런 / 실습 하네스

```bash
./lab.sh status     # 현재 전환 상태(모듈별 legacy|new, 신규 구현 수)
./lab.sh verify     # strangler 게이트 + gradle 수용기준 테스트
./lab.sh reset      # 시작 상태로 (전부 legacy, springboot 비움) — 실습 시작점
./lab.sh solve      # 정답 신규 구현 복원 + 전부 new (라이브 폴백·완성본)
```

contract 명령(`.agentic-dev/contract.json`):

```bash
./gradlew clean build -x test                                  # build
./gradlew test                                                 # proof (수용기준)
python3 sdd/99_toolchain/01_automation/run_strangler_check.py  # verify_dev (전환 게이트)
```

## 멱등성

`reset → (세 발화 또는 solve) → verify → reset` 을 몇 번 반복해도 매번 같은 결과로
수렴합니다. 시작 상태(전부 legacy)와 완료 상태(전부 new)는 물론, 전환 중간 상태
(도서만 new, 도서·회원만 new)에서도 수용기준이 항상 green 입니다. 검증 실적은 이
워크스페이스(JDK 17 + Gradle 8.5)에서 A(legacy)·B(부분)·C(전부 new)·D(reset) 전부 green 으로 확인했습니다.

## 왜 이렇게 동작하나

- 모든 요청은 컨트롤러(앞단 라우터 경유)를 통과하므로, 어느 구현이 활성이든 같은 수용기준을 통과합니다.
- legacy 와 new 가 공유 저장소(store/)를 쓰므로, 도서를 신규로 전환해도 아직 레거시인 대출이 같은 도서를 그대로 찾습니다(실제 전환의 공유 DB).
- 신규 대출은 `CatalogRouter` 로 도서·회원의 활성 구현을 받아 호출하므로, 부분 전환 중에도 모듈 간 호출이 끊기지 않습니다.
