import click
from typing import Dict, List
from datetime import datetime
from pathlib import Path
from appauto import __version__
from appauto.manager.config_manager import LoggingConfig, PytestConfig, TestDataConfig
from appauto.runners.pytest_runner import PytestRunner
from appauto.runners import ui_runner


@click.group()
@click.version_option(__version__, prog_name="appauto")
def cli():
    """appauto 命令行工具"""
    pass


@cli.group()
def env():
    """环境部署命令"""
    pass


@env.group()
def sglang():
    """管理 sglang 服务"""
    pass


@cli.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=["-h", "--help"])
)
@click.argument("mode", type=click.Choice(["pytest", "ui"]))
@click.option("--testpaths", required=True, help="Test paths (comma-separated)")
@click.option("--testclasses", help="test class")
@click.option("--testcases", help="Python functions pattern")
@click.option("--case-level", help="Case level marker")
# TODO 使用正确的 group & user
@click.option("--notify-group", default=None, help="Notify Group Chat ID")
# oc_69e39d9b1f06ea42ba76ce50e68acc77: sglang 8 卡测试
# @click.option("--notify-user", default="ou_de15ea583c7731052a0ab3bd370fc113", help="Notify User ID")
@click.option("--notify-user", default=None, help="Notify User ID")
@click.option("--interval", default=0, help="Delay in seconds between test cases. (Default: 0)")
@click.option("--repeat", default=1, help="Delay in seconds between test cases. (Default: 0)")
@click.option("--log-level", default="INFO", help="Log Level")
@click.option("--no-report", is_flag=True, help="Don't generate allure report (Default: False)")
@click.option("--keyword", default=None, help="Keyword (Default: None)")
@click.option("--collect-only", is_flag=True, help="Collect only test cases without executing (Default: False)")
@click.option("--report-server", default=None, help="Report Server (Default: None)")
@click.option("--report-url", default=None, help="Report URL (Default: None)")
@click.pass_context
def run(
    ctx,
    mode,
    testpaths,
    testclasses,
    testcases,
    case_level,
    log_level,
    notify_group,
    notify_user,
    interval,
    repeat,
    no_report,
    keyword,
    collect_only,
    report_server,
    report_url,
):
    """运行测试(pytest / ui)"""
    if collect_only:
        no_report = True
        notify_group = None
        notify_user = None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 配置日志
    LoggingConfig.config_logging(log_level=log_level, timestamp=timestamp)
    logger = LoggingConfig.get_logger()
    logger.info(f"Starting test run at {timestamp}")

    # 解析额外参数
    extra_args = parse_extra_args(ctx.args)
    logger.debug(f"Extra args: {extra_args}")

    # 配置测试数据
    TestDataConfig().config_testdata(
        mode=mode, testpaths=testpaths, log_level=log_level, timestamp=timestamp, **extra_args
    )

    # 运行测试
    if mode == "pytest":
        # 配置 pytest
        test_dir = Path(testpaths)
        PytestConfig(
            timestamp,
            test_dir,
            testclasses,
            testcases,
            log_level=log_level,
            no_report=no_report,
            collect_only=collect_only,
            case_level=case_level,
        ).config_pytest_ini()

        # 运行 pytest
        runner = PytestRunner(
            timestamp,
            log_level,
            notify_group,
            notify_user,
            repeat,
            interval,
            no_report,
            testpaths,
            keyword=keyword,
            report_server=report_server,
            report_url=report_url,
        )
        return_code = runner.run()
        if return_code != 0:
            raise click.ClickException(f"Tests failed with return code {return_code}")
    elif mode == "ui":
        ui_runner.run(testpaths, extra_args)
    else:
        logger.error("Unsupported test type.")


@env.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=["-h", "--help"])
)
@click.option("--host", required=True, help="远程主机 IP")
@click.option("--user", default="root", help="SSH 用户名")
@click.option("--password", help="SSH 密码")
@click.option("--component", required=True, help="部署组件名，例如: sg-server")
def deploy(host, user, password, component):
    """部署远程环境"""
    print("deploy_demo")


@sglang.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=["-h", "--help"])
)
@click.option("--mgt-ip", default="192.168.110.15", help="管理 IP 地址(Default: 192.168.110.15)")
@click.option("--conda-path", default="/home/zkyd/miniconda3/bin/conda", show_default=True, help="conda 路径")
@click.option("--conda-env-name", default="yanlong-ft", show_default=True, help="conda 环境名称")
@click.option(
    "--model-path", type=click.Choice(["DeepSeek-R1-GPTQ4-experts"]), required=True, help="模型路径（仅支持指定值）"
)
@click.option(
    "--amx-weight-path", type=click.Choice(["DeepSeek-R1-INT4"]), required=True, help="amx 权重路径（仅支持指定值）"
)
@click.option(
    "--served-model-name",
    type=click.Choice(["DeepSeek-R1"]),
    required=True,
    help="服务的模型名称（仅支持指定值）",
)
@click.option("--cpuinfer", type=int, required=True, help="CPU 推理线程数")
@click.option("--context-length", type=int, default=8192, show_default=True, help="上下文长度")
@click.option("--max-running-request", type=int, default=64, show_default=True, help="最大并发请求数")
@click.option("--max-total-tokens", type=int, default=65536, show_default=True, help="最大总 token 数")
@click.option("--mem-fraction-static", type=float, default=0.98, show_default=True, help="静态内存占用比例")
@click.option("--num-gpu-experts", type=int, default=1, show_default=True, help="GPU 专家数量")
@click.option(
    "--attention-backend",
    type=click.Choice(["flashinfer"]),
    default="flashinfer",
    show_default=True,
    help="注意力机制后端",
)
@click.option("--trust-remote-code", default=True, help="是否信任远程代码")
@click.option("--port", type=int, default=11002, show_default=True, help="服务端口")
@click.option("--host", default="0.0.0.0", show_default=True, help="绑定的主机地址")
@click.option(
    "--disable-shared-experts-fusion/--enable-shared-experts-fusion", default=True, help="是否禁用共享专家融合"
)
@click.option("--ssh-user", default="zkyd", show_default=True, help="SSH 用户名")
@click.option("--ssh-password", default="zkyd@12#$", help="SSH 密码")
@click.option("--ssh-port", type=int, default=22, show_default=True, help="SSH 端口")
def start(
    mgt_ip,
    ssh_user,
    ssh_password,
    ssh_port,
    conda_path,
    conda_env_name,
    model_path,
    amx_weight_path,
    served_model_name,
    cpuinfer,
    port,
    host,
    trust_remote_code,
    attention_backend,
    disable_shared_experts_fusion,
    num_gpu_experts,
    mem_fraction_static,
    max_total_tokens,
    max_running_request,
    context_length,
):
    """远程启动 sglang 服务"""
    logger = LoggingConfig.get_logger()
    from appauto.manager.server_manager import SGLangServer

    server = SGLangServer(
        mgt_ip=mgt_ip,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        conda_path=conda_path,
        conda_env_name=conda_env_name,
        model_path=model_path,
        amx_weight_path=amx_weight_path,
        served_model_name=served_model_name,
        cpuinfer=cpuinfer,
        port=port,
        trust_remote_code=trust_remote_code,
        disable_shared_experts_fusion=disable_shared_experts_fusion,
        ssh_port=ssh_port,
        host=host,
        attention_backend=attention_backend,
        num_gpu_experts=num_gpu_experts,
        mem_fraction_static=mem_fraction_static,
        max_total_tokens=max_total_tokens,
        max_running_request=max_running_request,
        context_length=context_length,
    )

    server.start(timeout_s=900)

    logger.info("✅ 已启动 sglang 服务!")


def parse_extra_args(args: List[str]) -> Dict[str, str | bool]:
    """解析额外参数
    支持以下格式：
    - --key=value
    - --flag (会被解析为 --flag=true)
    """
    return {arg.lstrip("-").split("=", 1)[0]: arg.split("=", 1)[1] if "=" in arg else "true" for arg in args or []}


if __name__ == "__main__":
    cli()
