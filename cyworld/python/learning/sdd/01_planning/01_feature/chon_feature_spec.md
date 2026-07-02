# 일촌(CHON) · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 원문: `sdd/00_sources/02_requirements/chon-relationship.md`

**AC-1** When 사용자가 다른 사용자에게 일촌 요청을 보내면, the system shall PENDING 상태의
일촌 요청을 생성하고 TTL(24시간)을 건다.

**AC-2** While 요청이 PENDING일 때, when 상대가 수락하면, the system shall 양방향 일촌
관계를 생성한다.

**AC-3** When 이미 일촌 관계이거나 PENDING 요청이 존재하는 대상에게 재요청하면, the system
shall 중복 생성 없이 기존 상태를 반환한다(멱등).

**AC-4** When 일촌 요청 TTL(24시간)이 지나면, the system shall 요청을 EXPIRED로 전이하고
재요청을 허용한다.

**AC-5** While 사용자의 일촌 수가 정원(750명)에 도달했을 때, when 새 요청을 수락하면,
the system shall 정원 초과로 거부한다.

**AC-6** When 사용자가 일촌을 해제(파일촌)하면, the system shall 양쪽 사용자 목록에서
동시에 관계를 제거한다.

**AC-7** While 일촌 관계가 아닐 때, when 일촌평 작성을 시도하면, the system shall
작성을 거부한다.

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1·AC-2 | `tests/test_chon.py::test_request_then_accept` |
| AC-3 | `tests/test_chon.py::test_request_idempotent` |
| AC-4 | `tests/test_chon.py::test_request_expiry` |
| AC-5 | `tests/test_chon.py::test_chon_capacity_750` |
| AC-6 | `tests/test_chon.py::test_unchon_removes_both_sides` |
| AC-7 | `tests/test_chon.py::test_chonpyeong_requires_chon` |
