# 투데이(TODAY) · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 원문: `sdd/00_sources/02_requirements/today.md`

**AC-1** When 사용자가 하루 중 처음으로 투데이를 등록하면, the system shall 해당 날짜에
등록 상태(recorded)를 저장한다.

**AC-2** While 같은 날짜에 이미 등록되어 있을 때, when 같은 사용자가 재등록을 요청하면,
the system shall 재등록 없이 기존 상태(already)를 반환한다(멱등).

**AC-3** When 날짜가 바뀐 뒤 사용자가 다시 등록을 요청하면, the system shall 새 날짜의
등록을 허용한다.

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_today.py::test_check_in_first_time` |
| AC-2 | `tests/test_today.py::test_check_in_idempotent_same_day` |
| AC-3 | `tests/test_today.py::test_check_in_new_day_allowed` |
