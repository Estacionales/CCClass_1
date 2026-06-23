#!/usr/bin/env bash
# 부동산 대규모 MSA 실습 하네스: 발화만으로 몇 번이든 같은 결과로 반복(멱등)하게 만든다.
#
# 실습은 이 폴더(시작 상태)에서 발화로 진행한다. PPT(15·16강)의 T1~T4 분담과 같다.
#   T1 @ingestion-dev  : ingestion-service + common (공유 계약 소유)
#   T2 @transaction-dev: transaction-service
#   T3 @analytics-dev  : analytics-service
#   T4 @platform-dev   : service-discovery + config-server + api-gateway (인프라)
#
#   ./lab.sh reset        깨끗한 시작 상태로 되돌린다. 코드 7개 모듈(common·ingestion·
#                         transaction·analytics·discovery·config·gateway 의 src/main/java)을
#                         비우고, 프론트(web)의 화면·컴포넌트·api 구현도 placeholder 로
#                         되돌린다. sdd 문서(00_sources·99_toolchain)·테스트(스펙)·
#                         build.gradle·게이트·인프라 설정(application.yml)·web 스캐폴딩은 그대로 둔다.
#                         (01_planning·02_plan 은 건드리지 않는다. 15강 산출물은 solve stage3 로 다룬다.)
#   ./lab.sh solve        정답 구현(solution/)을 복원한다(백엔드 7모듈 + web). 라이브가
#                         막혔을 때의 폴백, 또는 완성본 확인용.
#   ./lab.sh solve stage3 15강 산출물(sdd/01_planning + sdd/02_plan)을 복원한다.
#                         16강만 새로 시작할 때 ①의 명세·플랜(가드레일)을 되살린다.
#   ./lab.sh verify       아키텍처 게이트(7) + gradle 단위 테스트(8)를 돌린다(결정적·오프라인).
#   ./lab.sh e2e          7개 모듈(6서비스)을 docker compose로 부팅하고 게이트웨이 통과 E2E를 검증한다(Docker 필요).
#   ./lab.sh status       현재 상태(백엔드 코드 + 15강 산출물 + web 구현 존재 여부)를 보여준다.
#
#   ── 웹(Next.js) 명령 (Node 필요) ──────────────────────────────────
#   ./lab.sh web-reset    web/ 의 화면·컴포넌트·api 구현만 placeholder 로 되돌린다.
#                         (스캐폴딩·shadcn·계약 타입·프록시·E2E 스펙은 보존)
#   ./lab.sh web-solve    web/solution → web/src 로 정답 구현을 복원한다.
#   ./lab.sh web-install  web/ 의존성 설치 (lock 있으면 npm ci, 없으면 npm install).
#   ./lab.sh web-build    web/ 프로덕션 빌드 (next build).
#   ./lab.sh web-dev      web/ 개발 서버를 포그라운드로 띄운다 (강의·시연용, :3000).
#   ./lab.sh web-e2e      백엔드(docker compose 6서비스) + Next(:3000)를 띄우고
#                         Playwright 브라우저 E2E를 결정적으로 검증한 뒤 정리한다.
#                         (HEADED=1 이면 브라우저 창을 띄워 실행)
#
# reset→(발화로 구현 또는 solve)→verify→reset 을 반복해도 매번 동일하게 수렴한다.
# 테스트는 난수·실시간·네트워크에 의존하지 않는다(외부 data.go.kr 호출은 런타임 전용,
# 단위 테스트는 순수 도메인 로직만 검증). 그래서 결정적이다.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
# 코드 7개 모듈(PPT T1~T4). reset/solve 가 src/main/java 만 다루므로
# 게이트웨이 라우트 등 인프라 설정(application.yml)은 항상 보존된다.
DOMAIN=(common ingestion-service transaction-service analytics-service service-discovery config-server api-gateway)
: "${JAVA_HOME:=$(/usr/libexec/java_home -v 17 2>/dev/null || true)}"
export JAVA_HOME

reset() {
  for m in "${DOMAIN[@]}"; do rm -rf "$m/src/main/java/kr"; done
  echo "[reset] 코드 7개 모듈 구현 제거 완료. 시작 상태로 되돌렸습니다."
  echo "        남아 있는 것: sdd/00_sources·99_toolchain, src/test/ (스펙), 인프라 설정, build.gradle, 게이트."
  echo "        (15강 산출물 sdd/01_planning·02_plan 은 건드리지 않았습니다. 필요하면 solve stage3.)"
  # 프론트(web)도 같은 한 발로 시작 상태(placeholder)로 되돌린다(web/ 가 있을 때만).
  if [ -d "$WEB_DIR/placeholder" ]; then web_reset; fi
  status
}

solve() {
  for m in "${DOMAIN[@]}"; do
    if [ ! -d "solution/$m/kr" ]; then echo "[solve] solution/$m 스냅샷이 없습니다. 건너뜀." >&2; continue; fi
    rm -rf "$m/src/main/java/kr"
    mkdir -p "$m/src/main/java"
    cp -R "solution/$m/kr" "$m/src/main/java/"
  done
  echo "[solve] 정답 구현(백엔드 7모듈)을 복원했습니다."
  # 프론트(web)도 같은 한 발로 정답 복원(web/solution 이 있을 때만).
  if [ -d "$WEB_DIR/solution" ]; then web_solve; fi
  status
}

# 15강 산출물(01_planning + 02_plan)을 정답 스냅샷에서 복원한다.
# 16강만 새로 시작할 때 ①의 명세·플랜(가드레일)을 되살리는 용도다.
solve_stage3() {
  if [ ! -d "solution/sdd/01_planning" ]; then
    echo "[solve stage3] solution/sdd 스냅샷이 없습니다." >&2; exit 1
  fi
  for s in 01_planning 02_plan; do
    rm -rf "sdd/$s"
    cp -R "solution/sdd/$s" "sdd/$s"
  done
  echo "[solve stage3] 15강 산출물(sdd/01_planning + sdd/02_plan)을 복원했습니다."
  echo "              이제 이 명세·플랜이 16강 구현의 가드레일입니다."
}

status() {
  local n=0
  for m in "${DOMAIN[@]}"; do
    n=$((n + $(find "$m/src/main/java" -name '*.java' 2>/dev/null | wc -l | tr -d ' ')))
  done
  if [ "$n" != "0" ]; then
    echo "[status] 백엔드 코드 구현 있음 (${n}개 .java) → verify 가능"
  else
    echo "[status] 백엔드 코드 구현 없음(시작 상태) → 발화로 구현 필요 (또는 ./lab.sh solve)"
  fi
  if [ -f "sdd/01_planning/01_feature/realprice_ingest.md" ]; then
    echo "[status] 15강 산출물 있음 (sdd/01_planning·02_plan) → 16강 가드레일 준비됨"
  else
    echo "[status] 15강 산출물 없음(시작 상태) → 발화로 생성 (또는 16강만 시작 시 ./lab.sh solve stage3)"
  fi
  web_status
}

verify() {
  echo "[verify] 1/2 아키텍처 게이트"
  python3 sdd/99_toolchain/01_automation/run_arch_check.py
  echo "[verify] 2/2 gradle 단위 테스트"
  ./gradlew test --console=plain -q
  echo "[verify] 통과: 아키텍처 게이트 + 단위 8/8"
}

# 서비스 부팅 E2E: 6개 서비스를 docker compose로 띄우고 게이트웨이를 통해
# 수집(stub) → 멱등 적재 → CQRS 조회까지 결정적으로 검증한다(Docker 필요).
e2e() {
  echo "[e2e] bootJar 빌드"
  ./gradlew bootJar --console=plain -q
  echo "[e2e] 서비스 부팅 (eureka→config→도메인→gateway, healthcheck 순서)"
  docker compose up -d --build
  local rc=0
  bash e2e/smoke.sh || rc=$?
  echo "[e2e] 정리"
  docker compose down -v >/dev/null 2>&1 || true
  return $rc
}

# ───────────────────────── 웹(Next.js) 명령 ─────────────────────────
WEB_DIR="$HERE/web"

# web 의 "구현"으로 취급하는 파일들(화면·공용 컴포넌트·api 래퍼). 이것만 reset/solve 대상이다.
# 나머지(스캐폴딩·shadcn·계약 타입 types/format·프록시 route·E2E 스펙·설정)는 항상 보존된다.
WEB_IMPL=(
  "src/app/page.tsx"
  "src/app/ingest/page.tsx"
  "src/app/transactions/page.tsx"
  "src/app/analytics/page.tsx"
  "src/components/query-form.tsx"
  "src/lib/api.ts"
)

# placeholder/ (시작 스텁) → src 로 되돌린다. 백엔드 reset 이 src/main/java 만 비우고
# 테스트·인프라를 남기는 것과 동형: 프론트도 구현 파일만 스텁으로 바꾼다.
web_reset() {
  if [ ! -d "$WEB_DIR/placeholder" ]; then
    echo "[web-reset] placeholder 스냅샷이 없습니다(이 디렉토리는 정답 보존본일 수 있음). 건너뜀."
    return 0
  fi
  for f in "${WEB_IMPL[@]}"; do
    if [ -f "$WEB_DIR/placeholder/$f" ]; then
      mkdir -p "$WEB_DIR/$(dirname "$f")"
      cp "$WEB_DIR/placeholder/$f" "$WEB_DIR/$f"
    fi
  done
  echo "[web-reset] web 화면·컴포넌트·api 를 placeholder 로 되돌렸습니다."
  echo "            보존: layout·site-nav·ui(shadcn)·lib/types·lib/format·프록시 route·e2e 스펙·설정."
}

# solution/ (정답) → src 로 복원한다.
web_solve() {
  if [ ! -d "$WEB_DIR/solution" ]; then
    echo "[web-solve] web/solution 스냅샷이 없습니다(이 디렉토리는 정답 보존본일 수 있음). 건너뜀."
    return 0
  fi
  for f in "${WEB_IMPL[@]}"; do
    if [ -f "$WEB_DIR/solution/$f" ]; then
      mkdir -p "$WEB_DIR/$(dirname "$f")"
      cp "$WEB_DIR/solution/$f" "$WEB_DIR/$f"
    fi
  done
  echo "[web-solve] web 정답 구현(web/solution)을 복원했습니다."
}

# web 구현 상태를 보여준다(placeholder 인지 구현됐는지).
web_status() {
  if [ ! -d "$WEB_DIR/src" ]; then
    return 0
  fi
  if grep -q "TODO: 발화로 구현" "$WEB_DIR/src/lib/api.ts" 2>/dev/null; then
    echo "[status] web 프론트 구현 없음(placeholder) → 발화로 구현 필요 (검증: ./lab.sh web-e2e)"
  else
    echo "[status] web 프론트 구현 있음 → web-build / web-e2e 가능"
  fi
}

# Node 부재 시 web 명령만 친절히 실패시킨다(백엔드 verify/e2e 엔 영향 없음).
require_node() {
  if ! command -v node >/dev/null 2>&1; then
    echo "[web] Node.js 가 필요합니다. https://nodejs.org (LTS) 설치 후 다시 시도하세요." >&2
    echo "      (백엔드 명령 reset/solve/verify/e2e 는 Node 없이도 동작합니다.)" >&2
    exit 3
  fi
}

web_install() {
  require_node
  cd "$WEB_DIR"
  if [ -f package-lock.json ]; then
    echo "[web-install] npm ci (package-lock.json 기준 결정적 설치)"
    npm ci
  else
    echo "[web-install] npm install (lock 없음)"
    npm install
  fi
  cd "$HERE"
}

web_build() {
  require_node
  cd "$WEB_DIR"
  echo "[web-build] next build"
  npm run build
  cd "$HERE"
}

web_dev() {
  require_node
  cd "$WEB_DIR"
  echo "[web-dev] next dev (포그라운드, http://localhost:3000) — Ctrl+C 로 종료"
  exec npm run dev
}

# 백엔드(docker) + Next(:3000) 를 띄우고 Playwright 브라우저 E2E 를 돌린다.
# 결정적: stub 프로필 → transactions 5행(정상4+해제1), market-stats tradeCount=4, median 8.5억.
web_e2e() {
  require_node

  echo "[web-e2e] 1/6 bootJar 빌드"
  ./gradlew bootJar --console=plain -q

  echo "[web-e2e] 2/6 서비스 부팅 (docker compose, 6서비스)"
  docker compose up -d --build

  echo "[web-e2e] 3/6 게이트웨이 readiness 대기 (e2e/smoke.sh 로 백엔드 준비 확인)"
  local rc=0
  bash e2e/smoke.sh || rc=$?
  if [ "$rc" != "0" ]; then
    echo "[web-e2e] FAIL: 백엔드 준비 실패. 정리 후 종료."
    docker compose down -v >/dev/null 2>&1 || true
    return "$rc"
  fi

  # ── Next 준비 (의존성·빌드·기동) ─────────────────────────────
  cd "$WEB_DIR"
  if [ ! -d node_modules ]; then
    echo "[web-e2e] 4/6 web 의존성 설치"
    if [ -f package-lock.json ]; then npm ci; else npm install; fi
  fi
  echo "[web-e2e] 4/6 next build"
  npm run build

  echo "[web-e2e] 5/6 next start (백그라운드, :3000)"
  npm run start >/tmp/rf-next.log 2>&1 &
  local next_pid=$!

  # 3000 준비 대기 (최대 90초)
  local deadline=$((SECONDS + 90))
  until curl -fsS "http://localhost:3000" -o /dev/null 2>/dev/null; do
    if ! kill -0 "$next_pid" 2>/dev/null; then
      echo "[web-e2e] FAIL: next start 프로세스가 종료됨. 로그:"; cat /tmp/rf-next.log
      cd "$HERE"; docker compose down -v >/dev/null 2>&1 || true; return 1
    fi
    if [ $SECONDS -ge $deadline ]; then
      echo "[web-e2e] FAIL: Next(:3000) 준비 타임아웃. 로그:"; cat /tmp/rf-next.log
      kill "$next_pid" 2>/dev/null || true
      cd "$HERE"; docker compose down -v >/dev/null 2>&1 || true; return 1
    fi
    sleep 2
  done
  echo "[web-e2e] Next 준비 완료 (:3000)"

  echo "[web-e2e] 6/6 Playwright 브라우저 E2E"
  local pw_rc=0
  if [ -n "${HEADED:-}" ]; then
    npx playwright test --headed || pw_rc=$?
  else
    npx playwright test || pw_rc=$?
  fi

  echo "[web-e2e] teardown: Next 종료 + docker compose down -v"
  kill "$next_pid" 2>/dev/null || true
  wait "$next_pid" 2>/dev/null || true
  cd "$HERE"
  docker compose down -v >/dev/null 2>&1 || true

  if [ "$pw_rc" = "0" ]; then
    echo "[web-e2e] PASS: 브라우저 3시나리오(수집→거래조회→시세분석) 통과"
  else
    echo "[web-e2e] FAIL: Playwright 종료코드 $pw_rc"
  fi
  return "$pw_rc"
}

case "${1:-}" in
  reset)        reset ;;
  solve)        if [ "${2:-}" = "stage3" ]; then solve_stage3; else solve; fi ;;
  verify)       verify ;;
  e2e)          e2e ;;
  status)       status ;;
  web-reset)    web_reset ;;
  web-solve)    web_solve ;;
  web-install)  web_install ;;
  web-build)    web_build ;;
  web-dev)      web_dev ;;
  web-e2e)      web_e2e ;;
  *) echo "사용법: ./lab.sh {reset|solve|solve stage3|verify|e2e|status|web-reset|web-solve|web-install|web-build|web-dev|web-e2e}"; exit 2 ;;
esac
