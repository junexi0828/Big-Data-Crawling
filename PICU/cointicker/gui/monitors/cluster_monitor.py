"""
라즈베리파이 클러스터 모니터링 모듈
SSH를 통한 노드 상태 확인 및 제어
"""

import paramiko
import yaml
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from shared.logger import setup_logger
from shared.utils import get_cointicker_root
from gui.core.cache_manager import get_cache_manager

logger = setup_logger(__name__)


class ClusterMonitor:
    """클러스터 모니터 클래스"""

    def __init__(self, config_path: Optional[str] = None):
        """
        초기화

        Args:
            config_path: 클러스터 설정 파일 경로 (None이면 자동 탐지)
        """
        if config_path is None:
            # 공통 유틸리티 함수 사용하여 cointicker/config 찾기
            cointicker_root = get_cointicker_root()
            self.config_path = cointicker_root / "config" / "cluster_config.yaml"
        else:
            self.config_path = Path(config_path)
        self.config = self._load_config()
        self.ssh_clients: Dict[str, paramiko.SSHClient] = {}
        self.cache = get_cache_manager()
        # 클러스터 상태 캐시 TTL: 10초 (짧은 TTL로 최신 상태 유지)
        self.cache_ttl = 10.0

    def _load_config(self) -> dict:
        """설정 파일 로드"""
        try:
            config_file = self.config_path

            # 실제 파일이 없으면 예제 파일 사용
            if not config_file.exists():
                example_file = self.config_path.parent / (
                    self.config_path.name + ".example"
                )
                if example_file.exists():
                    logger.warning(
                        f"설정 파일이 없어 예제 파일을 사용합니다: {config_file}"
                    )
                    config_file = example_file
                else:
                    logger.error(f"설정 파일을 찾을 수 없습니다: {config_file}")
                    return {}

            with open(config_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    logger.warning(f"설정 파일이 비어있습니다: {config_file}")
                    return {}
                return yaml.safe_load(content) or {}
        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")
            return {}

    def _get_ssh_client(
        self, host: str, user: str, port: int = 22
    ) -> Optional[paramiko.SSHClient]:
        """
        SSH 클라이언트 가져오기 (재사용)

        Args:
            host: 호스트 주소
            user: 사용자명
            port: SSH 포트

        Returns:
            SSH 클라이언트 또는 None
        """
        key = f"{user}@{host}:{port}"

        if key in self.ssh_clients:
            return self.ssh_clients[key]

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, port=port, username=user, timeout=5)
            self.ssh_clients[key] = client
            return client
        except Exception as e:
            # SSH 연결 실패는 DEBUG 레벨로 변경 (반복 에러 방지)
            logger.debug(f"SSH 연결 실패 {host}: {e}")
            return None

    def execute_command(self, host: str, command: str) -> Dict[str, any]:
        """
        원격 명령어 실행

        Args:
            host: 호스트 주소
            command: 실행할 명령어

        Returns:
            실행 결과 딕셔너리
        """
        config = self.config.get("cluster", {})
        master = config.get("master", {})
        workers = config.get("workers", [])

        # 호스트 정보 찾기
        if host == master.get("ip") or host == master.get("hostname"):
            user = master.get("user", "pi")
            port = master.get("ssh_port", 22)
        else:
            worker = next(
                (
                    w
                    for w in workers
                    if w.get("ip") == host or w.get("hostname") == host
                ),
                None,
            )
            if not worker:
                return {"success": False, "error": f"호스트를 찾을 수 없습니다: {host}"}
            user = worker.get("user", "pi")
            port = worker.get("ssh_port", 22)

        client = self._get_ssh_client(host, user, port)
        if not client:
            return {"success": False, "error": "SSH 연결 실패"}

        try:
            stdin, stdout, stderr = client.exec_command(command, timeout=10)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode("utf-8")
            error = stderr.read().decode("utf-8")

            return {
                "success": exit_status == 0,
                "output": output,
                "error": error,
                "exit_status": exit_status,
            }
        except Exception as e:
            logger.error(f"명령어 실행 실패 {host}: {e}")
            return {"success": False, "error": str(e)}

    def get_node_status(self, host: str) -> Dict[str, any]:
        """
        노드 상태 확인 (캐싱 적용)

        Args:
            host: 호스트 주소

        Returns:
            노드 상태 정보
        """
        cache_key = f"cluster_node_status:{host}"

        # 캐시에서 가져오기
        cached_status = self.cache.get(
            cache_key,
            ttl_seconds=self.cache_ttl,
            factory=lambda: self._fetch_node_status(host),
        )

        return cached_status

    def _fetch_node_status(self, host: str) -> Dict[str, any]:
        """
        노드 상태 실제 조회 (캐싱 없이)

        Args:
            host: 호스트 주소

        Returns:
            노드 상태 정보
        """
        status = {
            "host": host,
            "online": False,
            "cpu_usage": None,
            "memory_usage": None,
            "disk_usage": None,
            "hadoop_status": None,
            "scrapy_status": None,
            "timestamp": datetime.now().isoformat(),
        }

        # 온라인 확인
        ping_result = self.execute_command(host, "echo 'online'")
        if ping_result.get("success"):
            status["online"] = True

            # CPU 사용률
            cpu_result = self.execute_command(
                host, "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
            )
            if cpu_result.get("success"):
                try:
                    status["cpu_usage"] = float(cpu_result["output"].strip())
                except:
                    pass

            # 메모리 사용률
            mem_result = self.execute_command(
                host, "free | grep Mem | awk '{printf \"%.1f\", $3/$2 * 100.0}'"
            )
            if mem_result.get("success"):
                try:
                    status["memory_usage"] = float(mem_result["output"].strip())
                except:
                    pass

            # 디스크 사용률
            disk_result = self.execute_command(
                host, "df -h / | tail -1 | awk '{print $5}' | sed 's/%//'"
            )
            if disk_result.get("success"):
                try:
                    status["disk_usage"] = float(disk_result["output"].strip())
                except:
                    pass

            # Hadoop 상태 (마스터 노드만)
            config = self.config.get("cluster", {})
            master = config.get("master", {})
            if host == master.get("ip") or host == master.get("hostname"):
                hadoop_result = self.execute_command(
                    host, "jps | grep -i namenode || echo 'not running'"
                )
                status["hadoop_status"] = (
                    "running"
                    if "namenode" in hadoop_result.get("output", "").lower()
                    else "stopped"
                )

            # Scrapy 프로세스 확인
            scrapy_result = self.execute_command(
                host, "ps aux | grep scrapy | grep -v grep | wc -l"
            )
            if scrapy_result.get("success"):
                try:
                    count = int(scrapy_result["output"].strip())
                    status["scrapy_status"] = (
                        f"{count} processes" if count > 0 else "stopped"
                    )
                except:
                    status["scrapy_status"] = "unknown"

        return status

    def get_all_nodes_status(self) -> List[Dict[str, any]]:
        """모든 노드 상태 확인"""
        config = self.config.get("cluster", {})
        master = config.get("master", {})
        workers = config.get("workers", [])

        nodes = []

        # 마스터 노드
        if master.get("ip"):
            nodes.append(self.get_node_status(master["ip"]))

        # 워커 노드
        for worker in workers:
            if worker.get("ip"):
                nodes.append(self.get_node_status(worker["ip"]))

        return nodes

    def start_spider(self, host: str, spider_name: str) -> Dict[str, any]:
        """
        Spider 시작

        Args:
            host: 호스트 주소
            spider_name: Spider 이름

        Returns:
            실행 결과
        """
        # scrapy.cfg가 있는 디렉토리로 이동
        command = (
            f"cd ~/cointicker/worker-nodes/cointicker && scrapy crawl {spider_name}"
        )
        return self.execute_command(host, command)

    def stop_spider(self, host: str, spider_name: str) -> Dict[str, any]:
        """
        Spider 중지

        Args:
            host: 호스트 주소
            spider_name: Spider 이름

        Returns:
            실행 결과
        """
        command = f"pkill -f 'scrapy crawl {spider_name}'"
        return self.execute_command(host, command)

    def restart_pipeline(self, host: str) -> Dict[str, any]:
        """
        파이프라인 재시작

        Args:
            host: 호스트 주소

        Returns:
            실행 결과
        """
        command = "cd ~/cointicker/master-node && python orchestrator.py &"
        return self.execute_command(host, command)

    def get_hdfs_status(self) -> Dict[str, any]:
        """HDFS 상태 확인"""
        config = self.config.get("cluster", {})
        master = config.get("master", {})

        if not master.get("ip"):
            return {"success": False, "error": "마스터 노드 설정이 없습니다"}

        # HDFS dfsadmin 리포트
        command = "hdfs dfsadmin -report"
        result = self.execute_command(master["ip"], command)

        return {
            "success": result.get("success", False),
            "report": result.get("output", ""),
            "timestamp": datetime.now().isoformat(),
        }

    def close(self):
        """SSH 연결 종료"""
        for client in self.ssh_clients.values():
            try:
                client.close()
            except:
                pass
        self.ssh_clients.clear()
