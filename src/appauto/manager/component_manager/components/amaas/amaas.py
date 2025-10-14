import os
from uuid import uuid4
from typing import List, Optional
from .base_component import BaseComponent
from .models import Worker, ModelStore, Model
from .scene import Scene
from .api_key import APIKey
from .dashboard import DashBoard
from .users import AMaaSUser
from ....config_manager.config_logging import LoggingConfig
from ....utils_manager.custom_list import CustomList

logger = LoggingConfig.get_logger()


class AMaaS(BaseComponent):
    OBJECT_TOKEN = None

    def __str__(self):
        return self.mgt_ip

    @property
    def init_model_store(self) -> ModelStore:
        """模型管理 - 模型中心"""
        params = dict(page=1, perPage=100, source="init")
        res = self.get("get_self", params, ModelStore.GET_URL_MAP)
        return ModelStore(self.mgt_ip, self.port, data=res.data.get("items"), amaas=self)

    @property
    def upload_model_store(self) -> ModelStore:
        """模型管理 - 私有模型"""
        params = dict(page=1, perPage=100, source="upload")
        res = self.get("get_self", params, ModelStore.GET_URL_MAP)
        return ModelStore(self.mgt_ip, self.port, data=res.data.get("items"), amaas=self)

    @property
    def model(self) -> Model:
        """模型管理-模型运行"""
        res = self.get("get_self", url_map=Model.GET_URL_MAP)
        return Model(self.mgt_ip, self.port, data=res.data.get("items"), amaas=self)

    @property
    def scene(self) -> Scene:
        """试验场景"""
        return Scene(self.mgt_ip, self.port, amaas=self)

    @property
    def workers(self) -> Optional[CustomList[Worker]]:
        """模型管理-模型加速"""
        res = self.get(alias="get_self", url_map=Worker.GET_URL_MAP)
        if res.retcode == 0:
            return CustomList(
                [
                    Worker(port=self.port, data=item, object_id=item.id, mgt_ip=self.mgt_ip, amaas=self)
                    for item in res.data.worker_resource_list
                ]
            )

    @property
    def api_keys(self) -> CustomList[APIKey]:
        """API 密钥"""
        params = dict(page=1, perpage=1000)
        res = self.get("get_self", url_map=APIKey.GET_URL_MAP, params=params)
        return CustomList(
            [APIKey(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self) for item in res.data.get("items")]
        )

    def create_api_key(self, name: str = None, expires_in=None, timeout: int = None):
        # TODO 时间戳有点诡异，是个 1970 年的时间戳？
        data = {"expires_in": expires_in or "30761967", "name": name or str(uuid4())}
        res = self.post("create", url_map=APIKey.POST_URL_MAP, json_data=data, timeout=timeout)
        return APIKey(self.mgt_ip, self.port, object_id=res.data.id, data=res.data, amaas=self)

    @property
    def users(self) -> List[AMaaSUser]:
        """用户管理"""
        params = dict(page=1, perpage=1000)
        res = self.get("get_self", url_map=AMaaSUser.GET_URL_MAP, params=params)
        return [
            AMaaSUser(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self)
            for item in res.data.get("items")
        ]

    def create_user(self, username, passwd, is_admin: bool, desc: str = None, timeout: int = None):
        data = {
            "username": username,
            "password": passwd,
            "is_admin": is_admin,
            "full_name": desc,
            "require_password_change": False,
        }
        res = self.post("create", url_map=AMaaSUser.POST_URL_MAP, json_data=data, timeout=timeout)
        return AMaaSUser(self.mgt_ip, self.port, object_id=res.data.id, data=res.data, amaas=self)

    def update_license(self, license_file_path, timeout: int = None) -> bool:
        logger.info(f"Uploading license file: {license_file_path}")
        if not os.path.exists(license_file_path):
            logger.error(f"License file not found: {license_file_path}")
            return False
        
        try:
            with open(license_file_path, 'rb') as file:
                # 使用文件对象而不是file.read()，这样httpx可以正确处理multipart格式
                files = {
                    'license_file': (os.path.basename(license_file_path), file, 'application/octet-stream')
                }
                logger.info(f"Uploading file: {os.path.basename(license_file_path)}")
                res = self.post("license", 
                            url_map={"license": "/auth/license"}, 
                            files=files,
                            timeout=timeout)
                #logger.info(f"License update response type: {type(res)}")
                #logger.info(f"License update response: {res}")
                
                # 根据后端响应格式调整判断逻辑
                # 后端返回的是 get_json_result(data='success')，应该包含 retcode=0
                if hasattr(res, 'retcode') and res.retcode == 0:
                    logger.info(f"License updated successfully: {license_file_path}")
                    return True
                else:
                    error_msg = getattr(res, 'retmsg', 'Unknown error')
                    logger.error(f"License update failed: {error_msg}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error updating license: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def auth_license(self, timeout: int = None) -> tuple:
        res = self.get("license", url_map={"license": "/auth/license"}, timeout=timeout)
        if res.retcode == 0:
            logger.info("License status retrieved successfully")
            return True, res.data.get("license_status", False)
        else:
            logger.error(f"Failed to get license status: {res.retmsg}")
            return False, False

