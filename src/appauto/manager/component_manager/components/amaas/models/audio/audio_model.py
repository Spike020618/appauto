from typing import Literal, List

from ..base import BaseModel, BaseModelStore
from ..model_instance import ModelInstance


class AudioModel(BaseModel):

    def __str__(self):
        return f"AudioModel(Name: {self.name}, ID: {self.object_id})"

    def check(self, worker_id: int, gpu_ids: List = None, tp: Literal[1, 2, 4, 8] = 1, timeout=None):
        data = {
            "id": self.model_store_id,
            "replicas": 1,
            "worker_id": str(worker_id),
            "access_limit": self.access_limit,
            "gpu_ids": gpu_ids,
            "fixed_backend_parameters": [],
            "backend_parameters": ["--tensor-parallel-size", "0" if gpu_ids else str(tp), "--max-total-tokens", "30"],
        }

        return self.post("check", url_map=BaseModelStore.POST_URL_MAP, json_data=data, timeout=timeout)

    def create_replica(
        self,
        worker_id: int,
        gpu_ids: List = None,
        tp: Literal[1, 2, 4, 8] = 1,
        wait_for_running=False,
        interval_s: int = 30,
        running_timeout_s: int = 600,
        timeout=None,
    ) -> ModelInstance:
        """
        - running_timeout_s: 等待 running 超时时间;
        - timeout: 单请求超时时间
        """

        assert tp or gpu_ids

        before = self.instances

        data = {
            "model_id": self.object_id,
            "replicas": 1,
            "worker_id": str(worker_id),
            "access_limit": self.access_limit,
            "gpu_ids": gpu_ids,
            "fixed_backend_parameters": [],
            "backend_parameters": ["--tensor-parallel-size", "0" if gpu_ids else str(tp), "--max-total-tokens", "30"],
        }

        self.post("create_replica", json_data=data, timeout=timeout)

        ins = [ins for ins in self.instances if ins not in before][0]

        if wait_for_running:
            ins.wait_for_running(interval_s, running_timeout_s)

        return ins
