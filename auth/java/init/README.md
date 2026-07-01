# Auth/OTP 데모 타깃 · Java (S05·07·08·09·10·11·12·16 공통 러닝 예제)

> 강의 데모용 **가상** 회원가입 OTP 서비스(자바·Spring Boot). 실재 개인정보 없음.
> 이 폴더는 자바 단일 언어로 자립합니다. 한 언어를 통째로 clone 해 실습합니다.

## 실행
```bash
./gradlew build -x test                  # build
./gradlew test                           # proof  → 10/10 PASS (tmp/proof-results.json)
./gradlew uiParity                        # verify_dev (회귀 게이트 재실행)
```

> 주의: 이 폴더(`init`·`learning`)는 **plan 시작점**이라 `src/main` 구현과 테스트가 비어 있습니다.
> 위 명령이 **10/10 으로 통과하는 완성 baseline 은 `complete/`** 이고, S05 환경구축은 거기서 확인합니다.
> 이 폴더는 S08~S09 에서 명세부터 직접 채워 갑니다.

## 강의 ↔ 단계 매핑
| 강의 | 단계 | 산출물 |
| --- | --- | --- |
| S05 환경구축 | clone→부팅 | `complete/` proof 10/10 self-test (이 폴더는 plan 시작점) |
| S07 01_planning | EARS spec | `sdd/01_planning/01_feature/auth_feature_spec.md` |
| S08 02_plan | todos·분할 | `sdd/02_plan/01_feature/auth_todos.md` |
| S09 03_build | 구현 | `src/main/java/com/datasense/auth/*` + `sdd/03_build/01_feature/auth.md` |
| S10 99_toolchain | 자동화 | `sdd/99_toolchain/01_automation/` |
| S11 04_verify | 회귀 4분면 | `sdd/04_verify/01_feature/auth.md` |
| S12 05_operate | 배포·롤백 | `sdd/05_operate/01_runbooks/auth-service.md` |
| S16 캡스톤 | 5단계 통합 | `sdd/` 전체 |

## 환경 경계 (정직)
실 강의 데모의 Playwright exactness·compose 부팅·GitHub Action 배포는 브라우저/Docker/CI를
요구합니다. 이 환경엔 없으므로 **백엔드 로직은 결정적 JUnit 테스트로 실제 검증**하고,
**화면 정합은 회귀 게이트(uiParity)**로, **배포는 로컬 스텁**으로 대체합니다(슬라이드에 명시된 경계).
