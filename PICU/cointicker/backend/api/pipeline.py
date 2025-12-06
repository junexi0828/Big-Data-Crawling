"""
파이프라인 제어 API 라우트
Kafka, HDFS, Spider 등 파이프라인 컴포넌트 제어
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
import subprocess
import sys
from pathlib import Path

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


def get_project_root() -> Path:
    """프로젝트 루트 경로 반환"""
    # backend/api/pipeline.py -> backend -> cointicker
    current_file = Path(__file__).resolve()
    return current_file.parent.parent.parent


@router.get("/kafka/status")
async def get_kafka_status():
    """Kafka Consumer 상태 조회"""
    try:
        project_root = get_project_root()
        kafka_consumer_path = project_root / "worker-nodes" / "kafka" / "kafka_consumer.py"

        # 프로세스 실행 여부 확인 (간단한 방법)
        import psutil
        kafka_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'kafka_consumer.py' in ' '.join(cmdline):
                    kafka_processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return {
            "success": True,
            "running": len(kafka_processes) > 0,
            "processes": kafka_processes,
            "consumer_path": str(kafka_consumer_path),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kafka 상태 조회 실패: {str(e)}")


@router.post("/kafka/start")
async def start_kafka_consumer():
    """Kafka Consumer 시작"""
    try:
        project_root = get_project_root()
        kafka_consumer_path = project_root / "worker-nodes" / "kafka" / "kafka_consumer.py"

        if not kafka_consumer_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Kafka Consumer 스크립트를 찾을 수 없습니다: {kafka_consumer_path}"
            )

        # 프로세스 시작
        process = subprocess.Popen(
            [sys.executable, str(kafka_consumer_path)],
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        return {
            "success": True,
            "message": "Kafka Consumer가 시작되었습니다",
            "pid": process.pid,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kafka Consumer 시작 실패: {str(e)}")


@router.post("/kafka/stop")
async def stop_kafka_consumer():
    """Kafka Consumer 중지"""
    try:
        import psutil

        # Kafka Consumer 프로세스 찾기
        kafka_pids = []
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'kafka_consumer.py' in ' '.join(cmdline):
                    kafka_pids.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if not kafka_pids:
            return {
                "success": True,
                "message": "실행 중인 Kafka Consumer가 없습니다",
                "stopped": 0,
            }

        # 프로세스 종료
        stopped_count = 0
        for pid in kafka_pids:
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                proc.wait(timeout=5)
                stopped_count += 1
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                try:
                    proc.kill()
                    stopped_count += 1
                except psutil.NoSuchProcess:
                    pass

        return {
            "success": True,
            "message": f"Kafka Consumer {stopped_count}개 중지 완료",
            "stopped": stopped_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kafka Consumer 중지 실패: {str(e)}")


@router.post("/kafka/restart")
async def restart_kafka_consumer():
    """Kafka Consumer 재시작"""
    try:
        # 먼저 중지
        stop_result = await stop_kafka_consumer()

        # 잠시 대기
        import time
        time.sleep(2)

        # 그 다음 시작
        start_result = await start_kafka_consumer()

        return {
            "success": stop_result.get("success") and start_result.get("success"),
            "message": "Kafka Consumer 재시작 완료",
            "stopped": stop_result.get("stopped", 0),
            "started_pid": start_result.get("pid"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kafka Consumer 재시작 실패: {str(e)}")


@router.get("/kafka/stats")
async def get_kafka_stats():
    """Kafka Consumer 통계 조회"""
    try:
        import psutil

        # Kafka Consumer 프로세스 찾기
        kafka_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'memory_info']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'kafka_consumer.py' in ' '.join(cmdline):
                    kafka_processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "create_time": proc.info['create_time'],
                        "memory_mb": proc.info['memory_info'].rss / (1024 * 1024) if proc.info.get('memory_info') else 0,
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return {
            "success": True,
            "running": len(kafka_processes) > 0,
            "processes": kafka_processes,
            "process_count": len(kafka_processes),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kafka 통계 조회 실패: {str(e)}")


@router.get("/kafka/topics")
async def get_kafka_topics():
    """Kafka 토픽 목록 조회"""
    try:
        from kafka import KafkaConsumer
        import re

        bootstrap_servers = ["localhost:9092"]
        topics_pattern = ["cointicker.raw.*"]

        # Consumer를 생성하여 토픽 목록 조회
        consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            consumer_timeout_ms=5000
        )

        # 모든 토픽 목록 조회
        all_topics = consumer.list_topics(timeout=5)
        topics_list = list(all_topics.topics.keys()) if all_topics else []

        # 패턴 매칭 (cointicker.raw.*)
        matching_topics = []
        for pattern in topics_pattern:
            # 와일드카드 패턴을 정규식으로 변환
            pattern_regex = pattern.replace(".", r"\.").replace("*", ".*").replace("?", ".")
            compiled_pattern = re.compile(pattern_regex)

            for topic in topics_list:
                if compiled_pattern.match(topic):
                    if topic not in matching_topics:
                        matching_topics.append(topic)

        consumer.close()

        return {
            "success": True,
            "all_topics": topics_list,
            "matching_topics": matching_topics,
            "subscribed_patterns": topics_pattern,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kafka 토픽 목록 조회 실패: {str(e)}")


@router.get("/kafka/consumer-groups")
async def get_kafka_consumer_groups():
    """Kafka Consumer Groups 상태 조회"""
    try:
        from kafka import KafkaConsumer

        bootstrap_servers = ["localhost:9092"]
        group_id = "cointicker-consumer"

        # Consumer를 생성하여 그룹 정보 조회
        consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            consumer_timeout_ms=5000
        )

        # 패턴 구독
        consumer.subscribe(pattern="cointicker.raw.*")

        # 잠시 대기하여 구독 완료
        import time
        time.sleep(1)

        # 구독 정보 조회
        subscription = consumer.subscription()
        assignment = consumer.assignment()

        consumer.close()

        return {
            "success": True,
            "group_id": group_id,
            "subscription": list(subscription) if subscription else [],
            "assignment": [
                {
                    "topic": tp.topic,
                    "partition": tp.partition,
                }
                for tp in assignment
            ] if assignment else [],
            "num_partitions": len(assignment) if assignment else 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consumer Groups 조회 실패: {str(e)}")


# ==================== HDFS API ====================

@router.get("/hdfs/status")
async def get_hdfs_status():
    """HDFS 상태 조회"""
    try:
        import socket

        # HDFS 포트 확인 (9000: NameNode, 9870: NameNode Web UI)
        ports = [9000, 9870]
        running_ports = []
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(("localhost", port))
                sock.close()
                if result == 0:
                    running_ports.append(port)
            except:
                pass

        # 프로세스 확인
        import psutil
        hdfs_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline:
                    cmdline_str = ' '.join(cmdline).lower()
                    if any(daemon in cmdline_str for daemon in ['namenode', 'datanode', 'secondarynamenode']):
                        hdfs_processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "daemon": next((d for d in ['namenode', 'datanode', 'secondarynamenode'] if d in cmdline_str), "unknown"),
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return {
            "success": True,
            "running": len(running_ports) > 0,
            "running_ports": running_ports,
            "processes": hdfs_processes,
            "namenode_port": 9000 if 9000 in running_ports else None,
            "namenode_web_ui_port": 9870 if 9870 in running_ports else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HDFS 상태 조회 실패: {str(e)}")


@router.post("/hdfs/start")
async def start_hdfs():
    """HDFS 데몬 시작"""
    try:
        project_root = get_project_root()

        # HDFSManager를 사용하여 데몬 시작
        # 실제로는 PipelineOrchestrator를 통해 시작해야 하지만,
        # 여기서는 간단하게 start-dfs.sh를 실행
        from pathlib import Path
        import os

        # HADOOP_HOME 찾기
        hadoop_home = os.environ.get("HADOOP_HOME")
        if not hadoop_home:
            # 프로젝트 경로에서 찾기
            possible_paths = [
                project_root.parent / "hadoop_project" / "hadoop-3.4.1",
                project_root / "hadoop_project" / "hadoop-3.4.1",
            ]
            for path in possible_paths:
                if path.exists():
                    hadoop_home = str(path)
                    break

        if not hadoop_home or not Path(hadoop_home).exists():
            raise HTTPException(
                status_code=404,
                detail="HADOOP_HOME을 찾을 수 없습니다. 환경 변수를 설정하거나 프로젝트 경로에 Hadoop이 설치되어 있어야 합니다."
            )

        start_dfs_script = Path(hadoop_home) / "sbin" / "start-dfs.sh"
        if not start_dfs_script.exists():
            raise HTTPException(
                status_code=404,
                detail=f"HDFS 시작 스크립트를 찾을 수 없습니다: {start_dfs_script}"
            )

        # HDFS 시작
        process = subprocess.Popen(
            ["bash", str(start_dfs_script)],
            cwd=str(Path(hadoop_home)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        return {
            "success": True,
            "message": "HDFS 데몬 시작 요청 완료",
            "pid": process.pid,
            "hadoop_home": hadoop_home,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HDFS 데몬 시작 실패: {str(e)}")


@router.post("/hdfs/stop")
async def stop_hdfs():
    """HDFS 데몬 중지"""
    try:
        from pathlib import Path
        import os

        project_root = get_project_root()

        # HADOOP_HOME 찾기
        hadoop_home = os.environ.get("HADOOP_HOME")
        if not hadoop_home:
            possible_paths = [
                project_root.parent / "hadoop_project" / "hadoop-3.4.1",
                project_root / "hadoop_project" / "hadoop-3.4.1",
            ]
            for path in possible_paths:
                if path.exists():
                    hadoop_home = str(path)
                    break

        if not hadoop_home or not Path(hadoop_home).exists():
            raise HTTPException(
                status_code=404,
                detail="HADOOP_HOME을 찾을 수 없습니다."
            )

        stop_dfs_script = Path(hadoop_home) / "sbin" / "stop-dfs.sh"
        if not stop_dfs_script.exists():
            raise HTTPException(
                status_code=404,
                detail=f"HDFS 중지 스크립트를 찾을 수 없습니다: {stop_dfs_script}"
            )

        # HDFS 중지
        process = subprocess.Popen(
            ["bash", str(stop_dfs_script)],
            cwd=str(Path(hadoop_home)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        return {
            "success": True,
            "message": "HDFS 데몬 중지 요청 완료",
            "pid": process.pid,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HDFS 데몬 중지 실패: {str(e)}")


@router.post("/hdfs/restart")
async def restart_hdfs():
    """HDFS 데몬 재시작"""
    try:
        # 먼저 중지
        stop_result = await stop_hdfs()

        # 잠시 대기
        import time
        time.sleep(2)

        # 그 다음 시작
        start_result = await start_hdfs()

        return {
            "success": stop_result.get("success") and start_result.get("success"),
            "message": "HDFS 데몬 재시작 완료",
            "stop_pid": stop_result.get("pid"),
            "start_pid": start_result.get("pid"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HDFS 데몬 재시작 실패: {str(e)}")


@router.get("/hdfs/stats")
async def get_hdfs_stats():
    """HDFS 통계 조회"""
    try:
        import psutil
        import socket

        # 포트 확인
        ports = [9000, 9870]
        running_ports = []
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(("localhost", port))
                sock.close()
                if result == 0:
                    running_ports.append(port)
            except:
                pass

        # 프로세스 정보
        hdfs_processes = []
        total_memory_mb = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'create_time']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline:
                    cmdline_str = ' '.join(cmdline).lower()
                    if any(daemon in cmdline_str for daemon in ['namenode', 'datanode', 'secondarynamenode']):
                        daemon_type = next((d for d in ['namenode', 'datanode', 'secondarynamenode'] if d in cmdline_str), "unknown")
                        memory_mb = proc.info.get('memory_info', {}).get('rss', 0) / (1024 * 1024) if proc.info.get('memory_info') else 0
                        total_memory_mb += memory_mb

                        hdfs_processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "daemon": daemon_type,
                            "memory_mb": memory_mb,
                            "create_time": proc.info.get('create_time'),
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return {
            "success": True,
            "running": len(running_ports) > 0,
            "running_ports": running_ports,
            "processes": hdfs_processes,
            "process_count": len(hdfs_processes),
            "total_memory_mb": total_memory_mb,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HDFS 통계 조회 실패: {str(e)}")


@router.get("/hdfs/files")
async def get_hdfs_files(hdfs_path: str = "/"):
    """HDFS 파일 목록 조회"""
    try:
        from shared.hdfs_client import HDFSClient

        client = HDFSClient(namenode="hdfs://localhost:9000")
        files = client.list_files(hdfs_path)

        return {
            "success": True,
            "path": hdfs_path,
            "files": files,
            "count": len(files) if files else 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HDFS 파일 목록 조회 실패: {str(e)}")

