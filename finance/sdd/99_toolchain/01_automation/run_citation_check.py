# -*- coding: utf-8 -*-
"""근거 인용 정확성 검사 (AC-3) — 근거 경로와 인용이 일치하는지 자동 점수화.

강의 슬라이드 11(04_verify 상담 분면)의 워크스루를 실제로 실행한다.
exit 0 = citation_exactness 만점.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 "..", "..", "..")))

from server.contexts.advisory import citation  # noqa: E402
from server.shared import rules  # noqa: E402

QUERY = '동의 완료자, 전입신고용 서류 발급 가능한가?'
MINWON = "전입신고"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--feature", default="eminwon")
    ap.parse_args(argv)

    steps, citations = rules.trace(MINWON)
    print(f'질의: "{QUERY}"')
    print("근거 경로 (검증):")
    for s in steps:
        print(f"  [{s.relation}] {s.src} → {s.dst}")
    ans = citation.answer(MINWON, eligible=True)
    print(f"\n응답 인용 ({len(citations)} hop, {len(citations)} citation):")
    for c in citations:
        print(f"  ✔ {c}")
    print("\n가드레일: 자격 미달 시 발급 거부 응답 → "
          + citation.answer(MINWON, eligible=False)["status"])
    exact = ans["exactness"]
    ok = exact.split("/")[0] == exact.split("/")[1]
    print(f"RESULT: citation_exactness {exact}  ·  {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
