# 방명록(GUESTBOOK) · 검증 (retained)

> proof: `python3 proof/run_proof.py` → 22/22 PASS (exit 0), 그 중 GUESTBOOK 4건.
> 실행: Python 3.14.6, `tmp/proof-results.json` (2026-07-02).

| 분면 | 검증 대상 | 수용기준 | 결과 |
| --- | --- | --- | --- |
| 기능 | 메시지 작성이 시간순으로 조회됨 | AC-1 | PASS · `test_post_message_ordered` |
| 검증 | 삭제는 주인·작성자만 허용, 제3자는 거부 | AC-2·AC-3 | PASS · `test_delete_permission` |
| 접근제어 | 비밀글은 주인·작성자 외 마스킹 | AC-4 | PASS · `test_secret_message_masking` |
| 검증 | 주인 답글은 메시지당 1개까지만 허용 | AC-5·AC-6 | PASS · `test_owner_reply_limit_one` |

## Residual Risk
- 없음(계획된 AC-1~AC-6 전부 구현·검증 완료).
