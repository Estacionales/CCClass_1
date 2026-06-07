# Auth/OTP 데모 타깃 (S05·07·08·09·10·11·12·16 공통 러닝 예제)

> 강의 데모용 **가상** 회원가입 OTP 서비스. 실재 개인정보 없음.
> SDD-stage 강의들이 공유하는 하나의 러닝 예제 — 각 강의가 한 단계씩 다룬다.

## 실행
```bash
pip install -r requirements.txt
python3 -m compileall -q server                              # build
python3 proof/run_proof.py                                   # proof  → 10/10 PASS
python3 sdd/99_toolchain/01_automation/run_ui_parity.py      # verify_dev (UI parity 1/1)
```

## 강의 ↔ 단계 매핑
| 강의 | 단계 | 산출물 |
| --- | --- | --- |
| S05 환경구축 | clone→부팅 | repo 부팅 + proof self-test |
| S07 01_planning | EARS spec | `sdd/01_planning/01_feature/auth_feature_spec.md` |
| S08 02_plan | todos·분할 | `sdd/02_plan/01_feature/auth_todos.md` |
| S09 03_build | 구현 | `contexts/auth/*` + `sdd/03_build/01_feature/auth.md` |
| S10 99_toolchain | 자동화 | `run_ui_parity.py` |
| S11 04_verify | 회귀 4분면 | `sdd/04_verify/01_feature/auth.md` |
| S12 05_operate | 배포·롤백 | `sdd/05_operate/01_runbooks/auth-service.md` |
| S16 캡스톤 | 5단계 통합 | `sdd/` 전체 |

## 환경 경계 (정직)
실 강의 데모의 Playwright exactness·compose 부팅·GitHub Action 배포는 브라우저/Docker/CI를
요구한다. 이 환경엔 없으므로 **백엔드 로직은 결정적 pytest로 실제 검증**하고,
**화면 정합은 HTML 스냅샷 parity**로, **배포는 로컬 스텁**으로 대체한다(슬라이드에 명시된 경계).
