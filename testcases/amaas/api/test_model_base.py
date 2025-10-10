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
    def test_hicache(self, model_store, tp, tokens):
        """
        hicache: 测试
        """
        if model_store.name == "GLM-4.5-Air-GPU-weight" and int(tp) > 2:
            pytest.skip(f"skip due to {model_store.name} and tp {tp}")
        result = cr.test_hicache(tp, model_store, tokens)
        # 简单的文件写入
        dc.check_final_item(result)

@allure.epic("TestInstances")
class TestInstances:
    @Requires.need_have(amaas, ["llm"])
    @pytest.mark.parametrize("model_store", cr.get_models_store("llm")[:1])
    @pytest.mark.parametrize("tp", DP.tp[:1])
    def test_instances(self, model_store, tp):
        """
        instances: 测试
        """
        if model_store.name == "GLM-4.5-Air-GPU-weight" and int(tp) > 2:
            pytest.skip(f"skip due to {model_store.name} and tp {tp}")
        result = cr.stop_all_instances(tp, model_store)
        dc.check_final_item(result)

    def validate_license_in_docker(container_id, license_path):
        """
        在Docker容器内验证许可证
        返回: (success, message) 元组
        """
        try:
            cmd = f"docker exec {container_id} python -m licenser.validator {license_path}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                logger.info(f"License validation output: {output}")
                return eval(output) if output else (False, "Empty output")
            else:
                error_msg = f"Command failed: {result.stderr}"
                logger.error(error_msg)
                return (False, error_msg)
                
        except subprocess.TimeoutExpired:
            error_msg = "License validation timeout"
            logger.error(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"License validation error: {str(e)}"
            logger.error(error_msg)
            return (False, error_msg)

@allure.epic("TestLicense")
class TestLicense:
    @pytest.mark.smoke
    @pytest.mark.parametrize("license_file_path", [
        "C:/Users/Spike/Downloads/LICENSE_3.txt",
        # 添加你需要测试的所有许可证文件名
    ])
    def test_license_files(self, license_file_path):
        """
        测试一堆许可证文件是否有效
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