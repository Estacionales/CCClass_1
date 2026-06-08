# agentic-dev-demo

SDD × Claude Code 강의의 **클론-앤-런 데모 타깃**입니다. `agentic-dev` 하네스
(`.claude`·`.codex`의 `skills/sdd` + `.agentic-dev/contract.json`)가 설치된 타깃 repo 두 개(`auth`·`finance`)와,
명세 유무를 직접 대조하는 핸즈온 데모(`sdd-contrast`)를 담고 있어, **클론하면 바로 build·proof·verify가 돕니다.**

> 모든 데이터는 강의용 **가상**입니다 — 실재 기관·시스템·개인정보·실명 없음.

## 타깃

| 폴더 | 예제 | 강의 |
| --- | --- | --- |
| `sdd-contrast/` | 명세 없이(vibe) vs 명세대로(SDD)를 같은 채점기로 직접 대조 — 핸즈온 | S03 |
| `auth/` | 회원가입 OTP 서비스 | S05·07·08·09·11·12·16 |
| `ecommerce/` | 이커머스 모놀리식(상품·재고·장바구니·주문·결제·체크아웃) DDD — 클린 스텁, `lab.sh`로 멱등 실습 | S10 |
| `library/` | 레거시 도서관(도서·회원·대출) strangler 전환 — 클린 스텁, 발화만으로 멱등 실습 | S13 |
| `finance/` | 금융·공공 대규모(MyLink) 동의 후 전자민원 자동 발급 | 금융·공공 데모 |
| `realestate/` | 부동산 실거래가 대규모 Spring Cloud MSA (단계형 SDD 핸즈온, data.go.kr 실연계) | S17 |

## 클론-앤-런

```bash
git clone https://github.com/say828/agentic-dev-demo.git
cd agentic-dev-demo/auth          # 또는 finance

pip install -r requirements.txt   # pytest
python3 -m compileall -q server                              # contract: build
python3 proof/run_proof.py                                   # contract: proof  (auth 10/10 · finance 14/14)
python3 sdd/99_toolchain/01_automation/run_ui_parity.py      # contract: verify_dev (auth)
# finance 의 verify_dev:
# python3 sdd/99_toolchain/01_automation/run_citation_check.py --feature eminwon
```

또는 `.agentic-dev/contract.json` 의 `commands.build / proof / verify_dev` 를 그대로 실행.

### sdd-contrast (S03 핸즈온)

다른 타깃과 달리 의존성·SDD 산출물이 없는 **경량 대조 데모**입니다. 학습자가 Claude Code로 `otp.py`를
직접 두 번(명세 없이 → 명세대로) 만들어 같은 채점기로 점수를 비교합니다. 상세는 `sdd-contrast/README.md`.

```bash
cd agentic-dev-demo/sdd-contrast   # 의존성 없음(파이썬 표준 라이브러리만)
python3 grade.py                   # 학습자가 만든 otp.py 채점 (라운드 1 → 1/4, 라운드 2 → 4/4)
python3 contrast.py                # 강사 폴백: vibe 1/4 vs SDD 4/4 결정적 재현
```

## 구조 (각 타깃)

- `.agentic-dev/contract.json` — build·proof·deploy_dev·verify_dev 명령
- `.claude/skills/sdd`·`.codex/skills/sdd` — 적용된 SDD 스킬
- `server/` — 도메인 구현 · `tests/` — proof 게이트(pytest)
- `sdd/` — SDD 5단계 산출물 (`00_sources → 01_planning → 02_plan → 03_build → 04_verify → 05_operate → 99_toolchain`)
- `proof/run_proof.py` — 결정적 게이트 러너

> `sdd-contrast/` 는 위 구조 대신 채점기(`acceptance.py`·`grade.py`)·명세(`spec.md`)·참고구현(`impls.py`)만 둔 경량 데모입니다.

## 경계

브라우저(Playwright exactness)·docker compose 부팅·GitHub Action 배포는 강사 환경에서.
이 repo는 백엔드 로직을 **결정적 pytest**로, 화면 정합을 **HTML 스냅샷 parity**로,
배포를 **로컬 스텁**으로 대체해 어디서든 클론 즉시 검증되도록 했습니다.
