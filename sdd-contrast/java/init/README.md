# sdd-contrast (자바) · 명세 유무 대조 핸즈온 (03강)

같은 채점기(`./gradlew grade`)로 OTP 구현 `MyOtp` 를 두 번 채점해, '명세가 결과를 가른다'를 눈으로 봅니다.

- **라운드 1 (바이브):** spec.md 를 보지 않고 Claude Code에 'OTP 만들어줘'만 시켜 `MyOtp` 를 만듭니다. 보통 1/4.
- **라운드 2 (SDD):** `sdd/01_planning/spec.md` 의 수용기준(AC-1~4)을 주고 다시 고칩니다. 4/4.

```bash
cd learning             # 실습 시작점 (MyOtp 가 바이브 수준 = 1/4, AC-2~4 TODO 힌트)
./gradlew grade         # 채점: 점수 1/4
# spec.md(AC-2 만료·AC-3 잠금·AC-4 멱등)를 읽고 MyOtp 를 고친 뒤
./gradlew grade         # 점수 4/4
./gradlew test          # 참고 대조(ContrastTest): SDD 4/4 > vibe
```

`learning`·`init`=실습 시작점(1/4, AC-2~4 TODO 힌트, 둘은 동일), `complete`=정답(4/4). 막히면 complete 와 비교하세요.
JDK 17 만 있으면 됩니다.
