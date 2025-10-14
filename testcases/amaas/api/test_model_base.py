"""
测试 models 的默认参数检查 / 运行 / 试验场景 / 停止
"""

import pytest
import allure

from appauto.manager.config_manager import LoggingConfig
from appauto.manager.utils_manager import Requires

from testcases.amaas.gen_data import amaas, DefaultParams as DP
from testcases.amaas.api.conftest import (
    CommonModelBaseRunner as cr,
    DoCheck as dc,
)

#logger = LoggingConfig.get_logger()


@allure.epic("TestHiCache")
class TestHiCache:
    @Requires.need_have(amaas, ["llm"])
    @pytest.mark.smoke
    @pytest.mark.parametrize("model_store", cr.get_models_store("llm"))
    @pytest.mark.parametrize("tp", DP.tp)
    @pytest.mark.parametrize("tokens", DP.tokens)
    @pytest.mark.parametrize("hicache", DP.hicache)
    def test_hicache(self, model_store, tp, tokens, hicache):
        """
        hicache: 测试
        """
        if model_store.name == "GLM-4.5-Air-GPU-weight" and int(tp) > 2:
            pytest.skip(f"skip due to {model_store.name} and tp {tp}")
        result = cr.test_hicache(tp, model_store, tokens, hicache)
        # 简单的文件写入
        dc.check_final_item(result)

@allure.epic("TestInstances")
class TestInstances:
    @Requires.need_have(amaas, ["llm"])
    @pytest.mark.parametrize("model_store", cr.get_models_store("llm"))
    @pytest.mark.parametrize("tp", DP.tp)
    def test_instances(self, model_store, tp):
        """
        instances: 测试
        """
        if model_store.name == "GLM-4.5-Air-GPU-weight" and int(tp) > 2:
            pytest.skip(f"skip due to {model_store.name} and tp {tp}")
        result = cr.test_instance(tp, model_store, "llm")
        dc.check_final_item(result)

@allure.epic("TestLicense")
class TestLicense:
    @pytest.mark.smoke
    @pytest.mark.parametrize("license_file_path", [
        "./license/LICENSE_1.txt",
        "./license/LICENSE_2.txt",
        
        "./license/LICENSE_4.txt",
        "./license/LICENSE_5.txt",
        "./license/LICENSE_6.txt",
        "./license/LICENSE_7.txt",
        "./license/LICENSE_3.txt",
        # 添加你需要测试的所有许可证文件名
    ])
    def test_license_files(self, license_file_path):
        """
        测试许可证文件是否有效
        """
        res = amaas.update_license(license_file_path)
        if res:
            res, auth = amaas.auth_license()
            if res:
                return auth
            else:
                return False
        else:
            return False