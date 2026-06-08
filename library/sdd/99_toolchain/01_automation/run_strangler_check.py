# -*- coding: utf-8 -*-
"""strangler 전환 게이트: migration.properties 를 읽어 모듈별 활성 구현과 전환 진척을 판정한다.

  - 세 모듈(books·members·loans)이 각각 legacy 인지 new 인지 보고한다.
  - new 로 지정된 모듈은 springboot 패키지에 해당 구현 클래스가 실제로 있는지 확인한다.
    (지정만 하고 구현이 없으면 라우터가 실패하므로, 게이트가 먼저 잡아낸다.)
  - 세 모듈이 모두 new 이고 구현이 모두 있으면 전환 완료(3/3)로 판정한다.

exit 0 = 설정과 구현이 일관됨(부분 전환도 일관되면 통과). exit 1 = 불일치.
전환 완료 여부는 메시지로 보고하되, 일관성만 맞으면 통과로 둔다(중간 단계도 정상 상태).
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
PROPS = ROOT / "src/main/resources/migration.properties"
SB = ROOT / "src/main/java/kr/elice/library/springboot"
MODULES = ["books", "members", "loans"]
CLASS = {"books": "NewBookService", "members": "NewMemberService", "loans": "NewLoanService"}


def read_modes():
    modes = {}
    for line in PROPS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        if k.startswith("module."):
            modes[k[len("module."):]] = v.strip().lower()
    return modes


def springboot_has(class_name):
    if not SB.exists():
        return False
    return any(re.search(rf"class\s+{class_name}\b", f.read_text(encoding="utf-8"))
               for f in SB.rglob("*.java"))


def main():
    modes = read_modes()
    print("[strangler] 모듈별 라우팅 상태")
    migrated = 0
    inconsistent = []
    for m in MODULES:
        mode = modes.get(m, "legacy")
        if mode == "new":
            migrated += 1
            ok = springboot_has(CLASS[m])
            mark = "OK" if ok else "구현 없음"
            if not ok:
                inconsistent.append(f"{m}=new 인데 springboot/{CLASS[m]} 없음")
            print(f"  - {m:8} → new (springboot/{CLASS[m]}: {mark})")
        else:
            print(f"  - {m:8} → legacy")
    print(f"[strangler] 전환 {migrated}/3" + (" · 전환 완료" if migrated == 3 else " · 진행 중"))
    if inconsistent:
        print("  불일치:")
        for x in inconsistent:
            print(f"    - {x}")
        print("RESULT: strangler FAIL")
        return 1
    print("RESULT: strangler PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
