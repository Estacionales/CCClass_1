# 알림(alerts) 도메인 · Acceptance Criteria (EARS) — 같은 5패턴

> 인증 말고도 같은 EARS 5패턴이 그대로 적용됨을 보이는 두 번째 예(개요만).

**AC-1** When 임계 이벤트가 발생하면, the system shall 구독자에게 알림을 1회 발송한다.

**AC-2** When 동일 이벤트가 재발생하면(중복), the system shall 멱등 키로 중복 발송을 막는다.

**AC-3** While 사용자가 알림을 끈 상태일 때, the system shall 발송하지 않는다.

> 본 데모의 실행 검증 대상은 auth 도메인이며, alerts 는 'EARS가 도메인 불문 동일하게
> 작동한다'를 보이는 계획 예시다(런타임 미구현).
