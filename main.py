"""TianShu2Markdown 可执行文件入口（PyInstaller 打包用）

双击 exe -> 自动打开浏览器 -> 启动本地转换服务
按 Ctrl+C 或关闭窗口停止服务
"""
import socket
import threading
import webbrowser

import uvicorn

from app import app

HOST = "127.0.0.1"
PORT = 8765
URL = f"http://{HOST}:{PORT}"


def is_port_busy() -> bool:
    """检测目标端口是否已被占用（避免重复启动）"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((HOST, PORT)) == 0


def open_browser() -> None:
    webbrowser.open(URL)


if __name__ == "__main__":
    print("=" * 46)
    print("  TianShu2Markdown · 天枢文档")
    print("=" * 46)

    if is_port_busy():
        print(f"[提示] 服务已在运行：{URL}")
        open_browser()
        input("按回车退出...")
        raise SystemExit(0)

    print(f"[启动] {URL}")
    print("       （保持窗口开启，按 Ctrl+C 停止服务）\n")

    # 延迟 2.5 秒打开浏览器，等待服务就绪
    threading.Timer(2.5, open_browser).start()
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
