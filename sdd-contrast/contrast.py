# -*- coding: utf-8 -*-
"""3강 데모: 같은 기능을 '명세 없이(vibe)' vs '명세 기반(SDD)'으로 채점해 대조한다.

실행: python3 contrast.py   (의존성 없음, 결정적)
exit 0. SDD 측은 4/4 통과해야 하고(게이트 통과), vibe 측의 누락이 그대로 드러난다.
"""
import sys

from acceptance import CRITERIA, run
from impls import SddOtp, VibeOtp


def _line(name, ok, note=""):
    mark = "PASS" if ok else "FAIL"
    tail = f"   ← {note}" if (note and not ok) else ""
    return f"  {name:<20} {mark}{tail}"


GAPS = {
    "AC-2 만료 OTP 거부": "만료된 코드도 통과 (만료를 명세 안 함)",
    "AC-3 5회 오류 잠금": "무한 시도 가능 (잠금을 명세 안 함)",
    "AC-4 재요청 멱등": "중복 가입 발생 (멱등을 명세 안 함)",
}


def main():
    print("같은 요구사항: '회원가입 OTP를 만들어줘'\n")

    vibe = run(lambda: VibeOtp())
    sdd = run(lambda: SddOtp())

    print("[ 명세 없이 — vibe coding ]")
    for name, _ in CRITERIA:
        print(_line(name, vibe[name], GAPS.get(name, "")))
    vpass = sum(vibe.values())
    print(f"  → {vpass}/{len(CRITERIA)} 통과. 게다가 검증 게이트(테스트)가 없어 이 빈틈이 그대로 배포됩니다.\n")

    print("[ 명세 기반 — SDD ]")
    for name, _ in CRITERIA:
        print(_line(name, sdd[name]))
    spass = sum(sdd.values())
    print(f"  → {spass}/{len(CRITERIA)} 통과. EARS 수용기준이 만료·잠금·멱등을 '맞는 동작'으로 정의하고, proof 게이트가 강제합니다.\n")

    print("교훈: '돌아간다'와 '맞다'는 다릅니다. 명세가 무엇이 맞는지 정의하고, 게이트가 그것을 검증합니다.")

    # SDD 측은 반드시 전부 통과해야 데모가 유효
    ok = spass == len(CRITERIA) and vpass < len(CRITERIA)
    print(f"\nRESULT: vibe {vpass}/{len(CRITERIA)} · SDD {spass}/{len(CRITERIA)}  ·  {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
