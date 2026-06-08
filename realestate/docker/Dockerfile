# 부동산 MSA 서비스 공용 이미지. bootJar 경로를 빌드 인자로 받아 실행합니다.
# (호스트에서 ./gradlew bootJar 로 만든 실행 가능 JAR을 복사)
# curl은 compose healthcheck(기동 순서 제어)에 사용합니다.
FROM eclipse-temurin:17-jre
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
ARG JAR
COPY ${JAR} app.jar
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
