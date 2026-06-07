# agentic-dev-demo

SDD × Claude Code 강의의 **클론-앤-런 데모 타깃**입니다. `agentic-dev` 하네스
(`.claude`·`.codex`의 `skills/sdd` + `.agentic-dev/contract.json`)가 설치된 타깃 repo 두 개를
담고 있어, **클론하면 바로 build·proof·verify가 돕니다.**

> 모든 데이터는 강의용 **가상**입니다 — 실재 기관·시스템·개인정보·실명 없음.

## 타깃

| 폴더 | 예제 | 강의 |
| --- | --- | --- |
| `auth/` | 회원가입 OTP 서비스 | S05·07·08·09·10·11·12·16 |
| `finance/` | 금융·공공 대규모(MyLink) 동의 후 전자민원 자동 발급 | S13 |

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

## 구조 (각 타깃)

- `.agentic-dev/contract.json` — build·proof·deploy_dev·verify_dev 명령
- `.claude/skills/sdd`·`.codex/skills/sdd` — 적용된 SDD 스킬
- `server/` — 도메인 구현 · `tests/` — proof 게이트(pytest)
- `sdd/` — SDD 5단계 산출물 (`00_sources → 01_planning → 02_plan → 03_build → 04_verify → 05_operate → 99_toolchain`)
- `proof/run_proof.py` — 결정적 게이트 러너

## 경계

브라우저(Playwright exactness)·docker compose 부팅·GitHub Action 배포는 강사 환경에서.
이 repo는 백엔드 로직을 **결정적 pytest**로, 화면 정합을 **HTML 스냅샷 parity**로,
배포를 **로컬 스텁**으로 대체해 어디서든 클론 즉시 검증되도록 했습니다.
