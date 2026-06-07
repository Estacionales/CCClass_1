# -*- coding: utf-8 -*-
"""근거 조회·자격 검색: 결정적 규칙 그래프 (민원 → 필요서류 → 근거규정 → 예외).

GraphRAG가 아니라 결정적 규칙 그래프로 '근거 규정 여러 단계 조회'를 구현한다.
강의 데모용 가상 규칙: 실재 기관·규정 해석이 아니다.
"""
from dataclasses import dataclass


class UnknownMinwon(Exception):
    """등록되지 않은 민원 유형."""


# 민원 유형 → 필요 서류
REQUIRED_DOCS = {
    "전입신고": ["주민등록표"],
    "사업자등록": ["사업자등록증", "임대차계약서"],
    "복지급여신청": ["주민등록표", "소득증명원"],
}

# 서류 → 근거 규정
DOC_BASIS = {
    "주민등록표": "전자정부법 §9",
    "사업자등록증": "부가가치세법 §8",
    "임대차계약서": "상가건물 임대차보호법 §3",
    "소득증명원": "국민기초생활보장법 §21",
}

# 근거 규정 → 예외 조건 (충족해야 발급 가능, None이면 예외 없음)
BASIS_EXCEPTION = {
    "전자정부법 §9": "세대주 동의",
    "부가가치세법 §8": None,
    "상가건물 임대차보호법 §3": None,
    "국민기초생활보장법 §21": "소득 기준 충족",
}


@dataclass(frozen=True)
class CitationStep:
    relation: str  # 필요서류 | 근거규정 | 예외
    src: str
    dst: str


def required_documents(minwon_type):
    docs = REQUIRED_DOCS.get(minwon_type)
    if docs is None:
        raise UnknownMinwon(minwon_type)
    return list(docs)


def exceptions_of(minwon_type):
    """이 민원 발급에 필요한 예외 조건 목록 (가드레일 판정용)."""
    conds = []
    for doc in required_documents(minwon_type):
        basis = DOC_BASIS.get(doc)
        exc = BASIS_EXCEPTION.get(basis) if basis else None
        if exc:
            conds.append(exc)
    return conds


def trace(minwon_type):
    """민원 → 필요서류 → 근거규정 → 예외 여러 단계 경로를 끝까지 따라간다.

    반환: (steps, citations)
      steps    : CitationStep 리스트 (관계 그래프)
      citations: 인용 순서대로의 노드 리스트 (서류 → 규정 → 예외)
    """
    docs = required_documents(minwon_type)
    steps, citations = [], []
    for doc in docs:
        steps.append(CitationStep("필요서류", minwon_type, doc))
        citations.append(doc)
        basis = DOC_BASIS.get(doc)
        if basis:
            steps.append(CitationStep("근거규정", doc, basis))
            citations.append(basis)
            exc = BASIS_EXCEPTION.get(basis)
            if exc:
                steps.append(CitationStep("예외", basis, exc))
                citations.append(exc)
    return steps, citations
