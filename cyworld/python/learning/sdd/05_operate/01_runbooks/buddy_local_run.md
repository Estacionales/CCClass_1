# 버디버디 메신저 · 로컬 실행 런북

> 이 저장소는 별도 DEV/PROD 인프라가 없는 로컬 단일 프로세스 데모다. "배포"는 로컬에서
> WSGI 개발 서버를 기동하는 것을 의미하며, 스테이지드 롤아웃(DEV→PROD) 게이트는 적용
> 대상이 아니다(`sdd/02_plan/01_feature/buddy_todos.md`의 Assumptions 참고).

## 실행
```bash
python3 -m pip install -r requirements.txt   # pytest만 필요
python3 -m server.web.app                    # → http://127.0.0.1:8000/
```

## 2인 로컬 대화 사용법
1. 서버 기동 후 브라우저 창(또는 시크릿 창) 두 개를 연다.
2. 창 A: `http://127.0.0.1:8000/messenger/yuna/minsu` (yuna로 접속)
3. 창 B: `http://127.0.0.1:8000/messenger/minsu/yuna` (minsu로 접속)
4. 양쪽 입력창에서 메시지를 보내면 최대 2초 이내에 상대 창에 자동으로 나타난다
   (2초 간격 폴링, WebSocket 아님 — `sdd/01_planning/02_screen/buddy_screen_spec.md`
   참고).
5. `http://127.0.0.1:8000/` 인덱스에서 시드 사용자별 미니홈피/메신저 링크로 이동 가능.
6. 새 버디를 시험하려면 `/messenger/<user>` 화면 하단 "버디 추가" 폼에 상대 아이디를
   입력 → 상대 쪽 화면에서 "받은 버디 요청"을 수락해야 대화가 가능해진다(비버디 간
   전송은 서버에서 무시된다, AC-5).

## 종료
- 터미널에서 `Ctrl+C`, 또는 포트 점유 프로세스를 찾아 종료:
  `netstat -ano | grep :8000` → 해당 PID를 `taskkill //PID <pid> //F` (Windows) /
  `kill <pid>` (POSIX).

## 검증 게이트
```bash
python3 proof/run_proof.py   # → 74/74 PASS(exit 0)가 완료 기준
```

## 알려진 제약
- 실 로그인/세션 없음 — URL 경로의 사용자 세그먼트가 신원을 대체한다.
- 인메모리 상태 — 서버 프로세스를 재시작하면 모든 버디 관계·대화·상태가 초기화된다
  (영속 저장소 없음, 데모 목적).
- `request`/`accept`/`reject`/`presence`는 예약어라 실제 사용자 아이디로 쓸 수 없다.
