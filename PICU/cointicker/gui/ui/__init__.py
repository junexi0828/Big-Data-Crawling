"""
UI 탭 모듈
각 탭을 별도 파일로 분리하여 코드 구조 개선
"""

from gui.ui.dashboard_tab import DashboardTab
from gui.ui.pipeline_status_widget import PipelineStatusWidget
from gui.ui.cluster_tab import ClusterTab
from gui.ui.tier2_tab import Tier2Tab
from gui.ui.modules_tab import ModulesTab
from gui.ui.control_tab import ControlTab
from gui.ui.config_tab import ConfigTab

__all__ = [
    "DashboardTab",
    "ClusterTab",
    "Tier2Tab",
    "ModulesTab",
    "ControlTab",
    "ConfigTab",
]
