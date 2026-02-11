import subprocess
import sys
import os
from pathlib import Path

def run_all():
    """Запуск всех сервисов"""
    backend_dir = Path(__file__).parent

    # Проверка виртуального окружения
    venv_python = backend_dir / 'venv' / 'Scripts' / 'python.exe'
    python_cmd = str(venv_python) if venv_python.exists() else 'python'

    print("Starting all services...")
    print(f"Using Python: {python_cmd}")

    processes = []

    try:
        # Запуск API сервера
        print("\n1. Starting API Server...")
        server_process = subprocess.Popen(
            [python_cmd, 'server.py'],
            cwd=backend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        processes.append(('API Server', server_process))

        # Запуск Webhook
        print("2. Starting Webhook Server...")
        webhook_process = subprocess.Popen(
            [python_cmd, 'webhook.py'],
            cwd=backend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        processes.append(('Webhook Server', webhook_process))

        # Запуск Telegram Bot
        print("3. Starting Telegram Bot...")
        bot_process = subprocess.Popen(
            [python_cmd, 'bot.py'],
            cwd=backend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        processes.append(('Telegram Bot', bot_process))

        print("\n✅ All services started!")
        print("\nPress Ctrl+C to stop all services...")

        # Ожидание
        for name, process in processes:
            process.wait()

    except KeyboardInterrupt:
        print("\n\nStopping all services...")
        for name, process in processes:
            print(f"Stopping {name}...")
            process.terminate()
        print("All services stopped.")
    except Exception as e:
        print(f"\nError: {e}")
        for name, process in processes:
            process.terminate()


if __name__ == "__main__":
    run_all()

