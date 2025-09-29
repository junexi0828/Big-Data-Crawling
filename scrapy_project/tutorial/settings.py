# Scrapy settings for tutorial project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "tutorial"

SPIDER_MODULES = ["tutorial.spiders"]
NEWSPIDER_MODULE = "tutorial.spiders"

ADDONS = {}

# ==============================================================================
# 🤖 윤리적 크롤링 설정 (Ethical Crawling Settings)
# ==============================================================================

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "tutorial (+http://www.yourdomain.com)"
# Set to some proper values! (이미지에서 강조된 부분)
# USER_AGENT = "Safari/537.36"

# Obey robots.txt rules - 웹사이트의 robots.txt 규칙을 준수
ROBOTSTXT_OBEY = True

# ==============================================================================
# 🚦 트래픽 제어 설정 (Traffic Control Settings)
# ==============================================================================

# 동시 요청 수 제한
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# 다운로드 지연 설정 (웹사이트 서버에 부담을 주지 않기 위해)
DOWNLOAD_DELAY = 3
# 다운로드 지연을 랜덤화 (0.5 * to 1.5 * DOWNLOAD_DELAY)
RANDOMIZE_DOWNLOAD_DELAY = True

# AutoThrottle 확장 활성화 (자동으로 지연 시간을 조절)
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "tutorial.middlewares.TutorialSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "tutorial.middlewares.TutorialDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# ==============================================================================
# 📦 Item Pipeline 설정 (Item Pipeline Settings)
# ==============================================================================

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "tutorial.pipelines.QuotesValidationPipeline": 200,  # 데이터 검증
    # "tutorial.pipelines.DuplicatesPipeline": 300,  # 중복 제거 (정규화 파이프라인에서 처리)
    "tutorial.pipelines.JsonWriterPipeline": 400,  # JSON 저장
    # "tutorial.pipelines.SQLitePipeline": 500,  # SQLite 저장
    # "tutorial.pipelines.MariaDBPipeline": 600,  # MariaDB 저장
    "tutorial.pipelines.NormalizedTutorialPipeline": 700,  # 정규화된 MariaDB 저장
}

# ==============================================================================
# 🗄️ MariaDB 연결 설정 (MariaDB Connection Settings)
# ==============================================================================

# MariaDB Connection String
CONNECTION_STRING = {
    'driver': 'mariadb',
    'user': 'crawler',
    'password': 'crawler+',
    'host': '127.0.0.1',  # localhost 대신 IP 주소 사용
    'port': 3306,
    'database': 'scrapy',
}

# ==============================================================================
# 🔄 중복 필터 설정 (Duplication Filter Settings)
# ==============================================================================

# 1. Global setting: change settings.py file and run again (이미지 방법 1)
# Disable the duplicate filter altogether! ← be careful about crawling loop!
# DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# ==============================================================================
# 💾 HTTP 캐시 설정 (HTTP Caching Settings)
# ==============================================================================

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600  # 1시간 캐시
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# ==============================================================================
# 🌐 기타 설정 (Other Settings)
# ==============================================================================

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

# 쿠키 비활성화 (개인정보 보호)
COOKIES_ENABLED = False

# 로그 레벨 설정
LOG_LEVEL = "INFO"

# 통계 수집 활성화
STATS_CLASS = "scrapy.statscollectors.MemoryStatsCollector"

# ==============================================================================
# 🎭 USER-AGENT 회전 설정 (User-Agent Rotation)
# ==============================================================================

# 다양한 USER-AGENT 목록
USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
]
