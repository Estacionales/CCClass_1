#!/usr/bin/env bash
# 서비스 부팅 E2E 스모크: 게이트웨이를 통해 수집 → 시세 조회까지 한 흐름을 검증한다.
# 결정적: ingestion이 stub 프로필이라 캔드 데이터(정상 4 + 해제 1)를 반환하므로
# 시세 통계는 항상 tradeCount=4, medianPriceWon=850,000,000 이다(해제 1건 제외).
set -uo pipefail
GW="${GW:-http://localhost:8080}"

echo "[e2e] 게이트웨이·디스커버리 준비 대기 (최대 210초)"
deadline=$((SECONDS + 210))
until curl -fsS -X POST "$GW/api/v1/ingest/apt-trade?lawdCd=11110&dealYmd=202405" -o /tmp/rf-ingest.json 2>/dev/null; do
  if [ $SECONDS -ge $deadline ]; then echo "[e2e] FAIL: 게이트웨이/수집이 준비되지 않음"; exit 1; fi
  sleep 5
done
echo "[e2e] ingest 응답: $(cat /tmp/rf-ingest.json)"

# 멱등 확인: 한 번 더 수집해도 결과가 같아야 한다(자연키 upsert)
curl -fsS -X POST "$GW/api/v1/ingest/apt-trade?lawdCd=11110&dealYmd=202405" -o /tmp/rf-ingest2.json 2>/dev/null || true
echo "[e2e] 재수집 응답(멱등): $(cat /tmp/rf-ingest2.json)"

echo "[e2e] 시세 통계 조회 (CQRS read model)"
if ! curl -fsS "$GW/api/v1/market-stats?sggCd=11110&dealYear=2024&dealMonth=5" -o /tmp/rf-stats.json 2>/dev/null; then
  echo "[e2e] FAIL: market-stats 조회 실패"; exit 1
fi
echo "[e2e] stats 응답: $(cat /tmp/rf-stats.json)"

python3 - <<'PY'
import json, sys
s = json.load(open('/tmp/rf-stats.json'))
ok = (s.get('tradeCount') == 4 and s.get('medianPriceWon') == 850000000)
print(f"[e2e] 검증: tradeCount={s.get('tradeCount')} (기대 4), "
      f"medianPriceWon={s.get('medianPriceWon')} (기대 850000000)")
if not ok:
    print("[e2e] FAIL: 기대값 불일치"); sys.exit(1)
print("[e2e] PASS: 게이트웨이→수집(stub)→멱등 적재→CQRS 조회 E2E 통과 (해제 1건 제외)")
PY
