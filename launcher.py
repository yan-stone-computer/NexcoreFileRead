"""NexcoreFileRead 启动器

功能：检测端口占用 -> 启动 uvicorn -> 自动打开浏览器
用法：python launcher.py   （start.bat 调用本文件）
"""
import socket
import subprocess
import sys
import threading
import webbrowser

HOST = "127.0.0.1"
PORT = 8765
URL = f"http://{HOST}:{PORT}"


def is_port_busy() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((HOST, PORT)) == 0


def main() -> None:
    print("=" * 46)
    print("  NexcoreFileRead · NexcoreFileRead")
    print("=" * 46)

    if is_port_busy():
        print(f"[提示] 服务已在运行：{URL}")
        print("       正在打开浏览器...")
        webbrowser.open(URL)
        return

    print(f"[启动] {URL}")
    print("       （保持本窗口开启，按 Ctrl+C 停止服务）\n")

    # 延迟 2 秒打开浏览器，等待服务就绪
    threading.Timer(2.0, lambda: webbrowser.open(URL)).start()

    import os

    try:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app:app",
                "--host",
                HOST,
                "--port",
                str(PORT),
            ],
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
    except KeyboardInterrupt:
        print("\n服务已停止。")
        return

    if proc.returncode != 0:
        print("\n[错误] 服务启动失败，请查看上方日志。")
        sys.exit(1)


if __name__ == "__main__":
    main()
