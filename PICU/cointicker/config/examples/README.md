# 설정 예제 파일

이 디렉토리는 설정 파일의 예제 템플릿을 포함합니다.

## 📋 사용 방법

### 설정 파일 생성

실제 설정 파일이 없을 때, 예제 파일을 복사하여 사용할 수 있습니다:

```bash
# 클러스터 설정
cp examples/cluster_config.yaml.example cluster_config.yaml

# 데이터베이스 설정
cp examples/database_config.yaml.example database_config.yaml

# Spider 설정
cp examples/spider_config.yaml.example spider_config.yaml

# Kafka 설정
cp examples/kafka_config.yaml.example kafka_config.yaml
```

### 자동 복사

GUI 애플리케이션이 시작될 때 자동으로 예제 파일에서 설정 파일을 생성합니다.

## 📁 파일 목록

- `cluster_config.yaml.example` - 클러스터 설정 예제
- `database_config.yaml.example` - 데이터베이스 설정 예제
- `spider_config.yaml.example` - Spider 설정 예제
- `kafka_config.yaml.example` - Kafka 설정 예제

---

**참고**: 예제 파일을 수정하지 마세요. 실제 설정 파일(`config/*.yaml`)을 수정하세요.
