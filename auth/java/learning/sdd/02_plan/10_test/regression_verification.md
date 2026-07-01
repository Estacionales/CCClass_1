# 회귀 검증 범위 (retained)

| 표면 | 분류 | 검증 |
| --- | --- | --- |
| 가입·OTP | direct | `OtpServiceTest`, `SignupFlowTest` |
| 로그인(기존) | shared | `RegressionTest` |
| 응답 계약(화면 parity 대체) | direct | `ContractParityTest` |

선정 근거: 회원가입은 계정 저장소를 로그인과 공유하므로 회귀 범위를 로그인까지 넓힌다.
