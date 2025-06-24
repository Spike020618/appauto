import allure

from appauto.manager.utils_manager.network_utils import NetworkUtils

from testcases.ftransformers.gen_data import sglang_server


class FTCommonCheck:
    @classmethod
    @allure.step("check_sglang_server_alive")
    def check_sglang_server_alive(self):
        assert sglang_server.exist(keyword="sglang.launch_server")
        assert NetworkUtils.check_reachable(sglang_server.mgt_ip, sglang_server.port)
