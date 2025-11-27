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
