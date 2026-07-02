# 04_verify · 도서·회원·대출 3모듈 strangler 전환 검증 요약

## 회귀 범위 선정

- 직접 대상: 신규 3개 서비스 클래스(`NewBookService`/`NewMemberService`/`NewLoanService`)와
  `migration.properties` 전환.
- 공유/연쇄 영향 대상으로 함께 검증: 라우터(`CatalogRouter`/`LoanRouter`/`Routing`), 컨트롤러
  (`BookController`/`MemberController`/`LoanController`), 예외 처리(`ApiExceptionHandler`) —
  전부 라우터 경유 호출이라 이 계층을 건너뛴 단위 테스트만으로는 회귀를 못 잡기 때문에
  MockMvc 기반 통합 테스트(`LibraryAcceptanceTest`, `AllNewModeTest`)로 검증했다.

## 실행한 검증

1. `./gradlew test` — 전환 전(`migration.properties` 전부 `legacy`, 최초 상태): **BUILD SUCCESSFUL**
   (기존 레거시 경로 회귀 없음 확인).
2. `migration.properties` 세 모듈 전부 `new` 로 전환 후 `./gradlew test` 재실행: **BUILD SUCCESSFUL**.
   - `LibraryAcceptanceTest` (모드 무관 채점기, 실제 `migration.properties` 값을 그대로 읽음):
     healthyFlow / ac1_loanLimit / ac2_overdueBlocks 전부 통과 → all-new 상태에서도 AC-1·AC-2 유지.
   - `AllNewModeTest` (`@TestPropertySource` 로 all-new 강제): `allNewBeansRegistered`,
     `newLoanUsesCatalogRouter`, `ac1_loanLimitEnforcedByNewImpl`, `ac2_overdueBlocksEnforcedByNewImpl`
     전부 통과 → 세 신규 빈이 모두 등록되고, `NewLoanService` 가 `CatalogRouter` 를 통해
     `NewBookService`/`NewMemberService` 와 정상 협력함을 별도로 확인.
3. `python sdd/99_toolchain/01_automation/run_strangler_check.py` (all-new 상태):
   ```
   - books    -> new (springboot/NewBookService: OK)
   - members  -> new (springboot/NewMemberService: OK)
   - loans    -> new (springboot/NewLoanService: OK)
   전환 3/3 · 전환 완료
   RESULT: strangler PASS
   ```

## 잔여 리스크

- 영속성 계층 변경 없음(인메모리 저장소 유지) — DEV/PROD 스키마 정합성 검증 대상 아님.
- 별도 DEV/PROD 배포 환경이 없는 인메모리 학습용 데모이므로 `05_operate` 갱신 대상 아님
  (배포 요청 없었음, 롤아웃 미실시).
- 신규 구현 3종은 레거시와 동일한 오류 메시지 문구를 사용해 사용자 노출 문자열 차이는 없음.
