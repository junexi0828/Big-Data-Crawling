# Scrapy settings for cointicker project

BOT_NAME = "cointicker"

SPIDER_MODULES = ["cointicker.spiders"]
NEWSPIDER_MODULE = "cointicker.spiders"

# ==============================================================================
# 윤리적 크롤링 설정
# ==============================================================================

# User-Agent 설정
USER_AGENT = "cointicker (+https://github.com/yourusername/cointicker)"

# robots.txt 준수
ROBOTSTXT_OBEY = True

# ==============================================================================
# 트래픽 제어 설정
# ==============================================================================

# 동시 요청 수
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# 다운로드 지연
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

# AutoThrottle 확장
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# ==============================================================================
# 쿠키 및 캐시 설정
# ==============================================================================

COOKIES_ENABLED = True
TELNETCONSOLE_ENABLED = False

# ==============================================================================
# HTTP 캐시 설정 (HTTP Caching Settings)
# ==============================================================================

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600  # 1시간 캐시
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# ==============================================================================
# 로깅 설정
# ==============================================================================

LOG_LEVEL = "INFO"
LOG_FILE = "logs/scrapy.log"

# ==============================================================================
# 파이프라인 설정
# ==============================================================================

ITEM_PIPELINES = {
    "cointicker.pipelines.ValidationPipeline": 300,
    "cointicker.pipelines.DuplicatesPipeline": 400,
    "cointicker.pipelines.HDFSPipeline": 500,
    # Kafka Pipeline (활성화됨)
    "cointicker.pipelines.kafka_pipeline.KafkaPipeline": 600,
}

# ==============================================================================
# 설정 파일 로드 (환경 변수 우선, 설정 파일 fallback)
# ==============================================================================
import os
import yaml
from pathlib import Path

def _load_kafka_config():
    """kafka_config.yaml에서 Kafka 설정 로드"""
    try:
        current_file = Path(__file__)
        config_file = current_file.parent.parent.parent / "config" / "kafka_config.yaml"
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if config and "kafka" in config:
                    kafka_config = config["kafka"]
                    topics_config = kafka_config.get("topics", {})
                    return {
                        "bootstrap_servers": kafka_config.get("bootstrap_servers", ["localhost:9092"]),
                        "topic_prefix": topics_config.get("raw_prefix", "cointicker.raw").split(".")[0],
                    }
    except Exception:
        pass
    return None

def _load_cluster_config():
    """cluster_config.yaml에서 HDFS 설정 로드"""
    try:
        current_file = Path(__file__)
        config_file = current_file.parent.parent.parent / "config" / "cluster_config.yaml"
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if config and "hadoop" in config:
                    hadoop_config = config["hadoop"]
                    hdfs_config = hadoop_config.get("hdfs", {})
                    return {
                        "namenode": hdfs_config.get("namenode", "hdfs://localhost:9000"),
                    }
    except Exception:
        pass
    return None

_kafka_config = _load_kafka_config()
_cluster_config = _load_cluster_config()

# Kafka 설정 (환경 변수 우선, 설정 파일 fallback, 기본값)
# Scrapy settings는 문자열을 기대하므로 문자열로 변환
_kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
if _kafka_bootstrap_servers:
    # 환경 변수는 문자열이므로 그대로 사용
    KAFKA_BOOTSTRAP_SERVERS = _kafka_bootstrap_servers
elif _kafka_config:
    bootstrap_servers = _kafka_config.get("bootstrap_servers", ["localhost:9092"])
    # 리스트인 경우 첫 번째 값 사용 (또는 쉼표로 구분된 문자열로 변환)
    if isinstance(bootstrap_servers, list):
        KAFKA_BOOTSTRAP_SERVERS = bootstrap_servers[0] if len(bootstrap_servers) == 1 else ",".join(bootstrap_servers)
    else:
        KAFKA_BOOTSTRAP_SERVERS = str(bootstrap_servers)
else:
    KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"  # 기본값

KAFKA_TOPIC_PREFIX = os.getenv("KAFKA_TOPIC_PREFIX", _kafka_config.get("topic_prefix", "cointicker") if _kafka_config else "cointicker")

# ==============================================================================
# HDFS 설정 (환경 변수 우선, 설정 파일 fallback, 기본값)
# ==============================================================================
HDFS_NAMENODE = os.getenv(
    "HDFS_NAMENODE",
    _cluster_config.get("namenode", "hdfs://localhost:9000") if _cluster_config else "hdfs://localhost:9000"
)

# ==============================================================================
# HDFS 자동 업로드 설정 (Self-healing 기능)
# ==============================================================================

# 최대 재시도 횟수 (Exponential Backoff)
HDFS_MAX_RETRIES = 3

# 초기 재시도 지연 시간 (초)
HDFS_INITIAL_DELAY = 2.0

# 재시도 간격 증가 배수 (Exponential Backoff)
# 예: 2초 -> 4초 -> 8초
HDFS_BACKOFF_FACTOR = 2.0

# HDFS 상태 확인 간격 (초)
# HDFS 연결 실패 시 주기적으로 연결 상태를 확인하고, 복구되면 자동으로 대기 파일을 업로드
HDFS_HEALTH_CHECK_INTERVAL = 300  # 5분

# ==============================================================================
# 다운로더 미들웨어 설정
# ==============================================================================

DOWNLOADER_MIDDLEWARES = {
    "cointicker.middlewares.CoinTickerDownloaderMiddleware": 543,
    "cointicker.middlewares.RotateUserAgentMiddleware": 400,  # User-Agent 회전
    "cointicker.middlewares.SeleniumMiddleware": 800,  # 높은 우선순위로 설정
}

# ==============================================================================
# Selenium 설정
# ==============================================================================

# Selenium을 사용할 도메인 리스트 (빈 리스트면 모든 도메인에서 사용 가능)
SELENIUM_ENABLED_DOMAINS = [
    "perplexity.ai",
    "www.perplexity.ai",
    "coinness.com",
    "www.coinness.com",
    "saveticker.com",
    "www.saveticker.com",
]

# 헤드리스 모드 사용 여부 (True: 브라우저 UI 없음, False: 브라우저 UI 표시)
SELENIUM_HEADLESS = True

# 페이지 스크롤 여부 (동적 콘텐츠 로드를 위해 페이지 끝까지 스크롤)
SELENIUM_SCROLL = True

# ChromeDriver 경로 (None이면 자동 감지)
# CHROMEDRIVER_PATH = None

# ==============================================================================
# 스파이더 미들웨어 설정
# ==============================================================================

SPIDER_MIDDLEWARES = {
    "cointicker.middlewares.CoinTickerSpiderMiddleware": 543,
}

# ==============================================================================
# 확장 설정
# ==============================================================================

EXTENSIONS = {
    "scrapy.extensions.telnet.TelnetConsole": None,
}

# ==============================================================================
# 요청 설정
# ==============================================================================

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# ==============================================================================
# USER-AGENT 회전 설정 (User-Agent Rotation)
# ==============================================================================

# 다양한 USER-AGENT 목록 (RotateUserAgentMiddleware에서 사용)
USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]
