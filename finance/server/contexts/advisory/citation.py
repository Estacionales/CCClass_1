# -*- coding: utf-8 -*-
"""상담 응답: 근거 규정을 여러 단계로 인용하고, 자격 미달이면 발급을 거부한다 (AC-3)."""
from server.shared import rules


def answer(minwon_type, *, eligible=True):
    """근거 경로(민원→서류→규정→예외)를 끝까지 인용한다.

    eligible=False(자격 미달)면 답을 지어내지 않고 거부한다 (가드레일).
    """
    steps, citations = rules.trace(minwon_type)
    if not eligible:
        return {
            "status": "refused",
            "reason": "자격 미달: 발급 거부",
            "citations": citations,
        }
    return {
        "status": "answered",
        "citations": citations,
        "steps": [(s.relation, s.src, s.dst) for s in steps],
        "exactness": f"{len(citations)}/{len(citations)}",
    }
