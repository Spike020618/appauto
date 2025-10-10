from typing import Literal
from functools import cached_property
from appauto.manager.client_manager import BaseLinux
from appauto.manager.utils_manager.format_output import remove_line_break

from .components.docker import AMaaSDocker


class AMaaSNodeCli(BaseLinux):
    def __init__(self, mgt_ip, ssh_user="qujing", ssh_password="madsys123", ssh_port=22):
        self.docker = AMaaSDocker(mgt_ip, ssh_user, ssh_password, ssh_port)
        super().__init__(mgt_ip, ssh_user, ssh_password, ssh_port)

    @cached_property
    def nic_mac_addr(self) -> str:
        cmd = (
            'ip link show | awk \'/^[0-9]+: / { dev = $2; sub(/:/, "", dev); next; } '
            "/link\/ether/ && dev !~ /^(lo|docker|veth)/ { print toupper($2); exit; }'"
        )
        _, res, _ = self.run(cmd)

        return remove_line_break(res)

    def have_pid(self, pid: int) -> bool:
        cmd = f"docker exec zhiwen-ames ps -p {pid} "
        rc, _, _ = self.run(cmd)

        return not rc

    def instance_check_and_stop(self, ids: list) -> list:
        """
        检查每个 id 对应的容器是否存在，存在则停止，并返回操作结果。
        返回值示例: [{"id": "xxx", "existed": True, "stopped": True}, ...]
        """
        results = []
        for id in ids:
            try:
                # 检查容器是否存在
                cmd_check = (
                    f'docker inspect {id} >/dev/null 2>&1 && echo "True" || echo "False"'
                )
                _, res, _ = self.run(cmd_check)
                existed = remove_line_break(res).strip() == "True"
                stopped = False
                if existed:
                    # 停止容器
                    cmd_stop = f'docker stop {id}'
                    self.run(cmd_stop)
                    stopped = True
                results.append({"id": id, "existed": existed, "stopped": stopped})
            except Exception as e:
                results.append({"id": id, "existed": False, "stopped": False, "error": str(e)})
        return results

    def run_as_perf(
        self,
        model_name,
        tp: Literal[1, 2, 4, 8],
        dp: int = 2,
    ):
        """
        以性能测试参数拉起模型
        """
        ...
