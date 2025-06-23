import pytest

from appauto.manager.client_manager import BaseLinux
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()

linux = BaseLinux("192.168.110.15", "zkyd", "zkyd@12#$")


class TestBaseLinux:
    def test_grep_pid(self):
        pids = linux.grep_pid("sglang.launch_server")
        logger.info(pids)
        assert pids

    def test_stop_process_by_keyword(self):
        linux.stop_process_by_keyword("sglang.launch_server", force=True)

    def test_conda_env_list(self):
        lts = linux.conda_env_list(conda_path="/home/zkyd/miniconda3/bin/conda")
        logger.info(lts)
        # assert lts
