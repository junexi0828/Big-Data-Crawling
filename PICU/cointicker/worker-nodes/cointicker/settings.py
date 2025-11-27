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
    # Kafka Pipeline (선택적, 설정에서 활성화)
    # "cointicker.pipelines.kafka_pipeline.KafkaPipeline": 600,
}

# Kafka 설정 (선택적)
# KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"  # 또는 ["localhost:9092", "192.168.1.100:9092"]
# KAFKA_TOPIC_PREFIX = "cointicker"

# ==============================================================================
# 다운로더 미들웨어 설정
# ==============================================================================

DOWNLOADER_MIDDLEWARES = {
    "cointicker.middlewares.CoinTickerDownloaderMiddleware": 543,
}

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
