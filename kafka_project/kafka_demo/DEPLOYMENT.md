# Runnable JAR 파일 배포 가이드

강의 슬라이드를 기반으로 한 Runnable JAR 파일 생성 및 배포 가이드입니다.

## 📦 Runnable JAR 파일 생성

### 방법 1: Maven Shade Plugin 사용 (권장)

프로젝트의 `pom.xml`에 이미 Maven Shade Plugin이 설정되어 있습니다.

```bash
cd kafka_project/kafka_demo
mvn clean package
```

생성된 JAR 파일:
- `target/kafka.demo-0.0.1-SNAPSHOT.jar` (실행 가능한 JAR)

### 방법 2: Eclipse IDE 사용

1. **프로젝트 우클릭** → `Export` → `Java` → `Runnable JAR file`
2. **Launch configuration** 선택: `Producer (1) - kafka.demo` (또는 원하는 메인 클래스)
3. **Export destination** 지정: 예) `D:\Downloads\kafka-producer.jar`
4. **Library handling** 선택: `Copy required libraries into a sub-folder next to the generated JAR`
5. **Finish** 클릭

생성된 파일:
- `kafka-producer.jar` (실행 가능한 JAR)
- `kafka-producer_lib/` (의존성 라이브러리 폴더)

## 🚀 원격 서버로 배포

### 1. JAR 파일 및 라이브러리 폴더 전송

**SFTP 사용:**
```bash
sftp bigdata@bigpie3
put kafka-producer.jar
put -r kafka-producer_lib /home/bigdata/kafka-producer_lib
```

**또는 SCP 사용:**
```bash
scp kafka-producer.jar bigdata@bigpie3:~/
scp -r kafka-producer_lib bigdata@bigpie3:~/kafka-producer_lib
```

### 2. 원격 서버에서 실행

**Linux/macOS:**
```bash
java -cp "kafka-producer.jar:kafka-producer_lib/*" bigdata.kafka.demo.Producer
```

**Windows:**
```bash
java -cp "kafka-producer.jar;kafka-producer_lib/*" bigdata.kafka.demo.Producer
```

## 📝 주의사항

1. **bootstrap-server 형식 확인**: JAR 파일 실행 전에 `bootstrap-server` 주소가 올바른 형식인지 확인하세요.
2. **의존성 라이브러리**: `_lib` 폴더와 JAR 파일을 함께 전송해야 합니다.
3. **Java 버전**: 원격 서버에 Java 8 이상이 설치되어 있어야 합니다.
4. **Kafka 서버**: 원격 서버에서 Kafka 서버에 접근 가능해야 합니다.

## 🔧 다른 메인 클래스 실행

다른 클래스를 실행하려면 클래스 이름만 변경하면 됩니다:

```bash
# CallbackProducer 실행
java -cp "kafka-producer.jar:kafka-producer_lib/*" bigdata.kafka.demo.CallbackProducer

# KeyedCallbackProducer 실행
java -cp "kafka-producer.jar:kafka-producer_lib/*" bigdata.kafka.demo.KeyedCallbackProducer

# Consumer 실행
java -cp "kafka-producer.jar:kafka-producer_lib/*" bigdata.kafka.demo.Consumer

# PartitionedConsumer 실행
java -cp "kafka-producer.jar:kafka-producer_lib/*" bigdata.kafka.demo.PartitionedConsumer
```

## 📊 실행 결과 예시

```
Hello, from Java: Thu May 22 00:16:20 KST 2025
Hello, from Java: Thu May 22 00:16:55 KST 2025
Hello, from Java: Thu May 22 00:31:59 KST 2025
```

## ⚠️ SLF4J 경고

실행 시 다음과 같은 경고가 나타날 수 있습니다:
```
SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".
SLF4J: Defaulting to no-operation (NOP) logger implementation
```

이는 로깅 구현체가 없어서 발생하는 경고이며, 애플리케이션 실행에는 문제가 없습니다.
로깅을 사용하려면 `log4j-slf4j2-impl` 의존성이 포함되어 있는지 확인하세요.

