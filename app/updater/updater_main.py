"""Standalone updater tool."""
import os
import sys
import time
import subprocess
import argparse
import psutil

from app.core.update_checker import UpdateChecker
from app.core.update_downloader import UpdateDownloader
from app.core.update_security import verify_sha256


APP_NAME = "FileRenamer"


def get_default_install_dir() -> str:
    """Return the expected per-user install directory."""
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        if os.path.exists(os.path.join(exe_dir, f"{APP_NAME}.exe")):
            return exe_dir

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return os.path.join(local_app_data, "Programs", APP_NAME)

    return os.path.join(os.path.expanduser("~"), "AppData", "Local", "Programs", APP_NAME)


def wait_for_process_exit(pid: int | None, timeout: int = 30) -> bool:
    """Wait for the main app process to terminate."""
    if not pid:
        return True

    try:
        process = psutil.Process(pid)
        for _ in range(timeout):
            if not process.is_running():
                return True
            time.sleep(1)
        return False
    except psutil.NoSuchProcess:
        return True


def download_latest_package() -> str | None:
    """Download the latest update package when the updater is run directly."""
    checker = UpdateChecker()
    manifest = checker.check_for_update()
    if not manifest:
        print("No update is available.")
        return None

    if not manifest.package_url:
        print("Latest release does not include FileRenamer-Setup.exe.")
        return None

    print(f"Downloading FileRenamer v{manifest.version}...")
    downloader = UpdateDownloader()
    package_path = downloader.download_package(
        manifest.package_url,
        progress_callback=lambda percent: print(f"Downloading: {percent}%"),
    )

    if manifest.sha256:
        print("Verifying update package...")
        if not verify_sha256(package_path, manifest.sha256):
            downloader.cleanup()
            raise RuntimeError("Update package verification failed (hash mismatch).")
    else:
        print("Warning: release did not provide SHA-256; installing downloaded GitHub release asset.")

    return package_path


def run_installer(package_path: str, restart: bool, install_dir: str) -> int:
    """Run the downloaded installer silently and optionally restart the app."""
    print(f"Running installer: {package_path} --silent")
    result = subprocess.run([package_path, "--silent"], check=False)
    if result.returncode != 0:
        print(f"Installer failed with exit code {result.returncode}")
        return result.returncode

    print("Update installed successfully.")
    if restart:
        app_exe = os.path.join(install_dir, f"{APP_NAME}.exe")
        if os.path.exists(app_exe):
            print(f"Restarting app: {app_exe}")
            subprocess.Popen([app_exe], start_new_session=True)

    return 0


def main():
    parser = argparse.ArgumentParser(description="FileRenamer Auto-Updater")
    parser.add_argument("--package", help="Path to the update installer")
    parser.add_argument("--parent-pid", type=int, help="PID of the main app")
    parser.add_argument("--install-dir", default=get_default_install_dir(), help="App installation directory")
    parser.add_argument("--restart", action="store_true", help="Restart app after update")
    
    args = parser.parse_args()

    # 1. Wait for main app to exit
    if args.parent_pid:
        print(f"Waiting for parent process {args.parent_pid} to exit...")
    if not wait_for_process_exit(args.parent_pid):
        print("Error: Parent process did not exit in time.")
        sys.exit(1)

    package_path = args.package or download_latest_package()
    if not package_path:
        sys.exit(0)

    try:
        sys.exit(run_installer(package_path, args.restart, args.install_dir))
    except Exception as e:
        print(f"Error during update: {e}")
        sys.exit(1)
    finally:
        # 4. Cleanup temp package if needed (optional as downloader does it)
        pass


if __name__ == "__main__":
    main()
