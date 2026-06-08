"""Standalone updater tool."""
import os
import sys
import time
import subprocess
import argparse
import psutil


def wait_for_process_exit(pid: int, timeout: int = 30) -> bool:
    """Wait for the main app process to terminate."""
    try:
        process = psutil.Process(pid)
        for _ in range(timeout):
            if not process.is_running():
                return True
            time.Sleep(1)
        return False
    except psutil.NoSuchProcess:
        return True


def main():
    parser = argparse.ArgumentParser(description="FileRenamer Auto-Updater")
    parser.add_argument("--package", required=True, help="Path to the update installer")
    parser.add_argument("--parent-pid", type=int, required=True, help="PID of the main app")
    parser.add_argument("--install-dir", required=True, help="App installation directory")
    parser.add_argument("--restart", action="store_true", help="Restart app after update")
    
    args = parser.parse_args()

    # 1. Wait for main app to exit
    print(f"Waiting for parent process {args.parent_pid} to exit...")
    if not wait_for_process_exit(args.parent_pid):
        print("Error: Parent process did not exit in time.")
        sys.exit(1)

    # 2. Run installer silently
    print(f"Running installer: {args.package} --silent")
    try:
        # We use shell=True or call directly. 
        # Since it's an EXE, we can just call it.
        # --silent is a flag we'll add to InstallerStub
        cmd = [args.package, "--silent"]
        result = subprocess.run(cmd, check=True)
        
        if result.returncode == 0:
            print("Update installed successfully.")
            
            # 3. Relaunch app if requested
            if args.restart:
                app_exe = os.path.join(args.install_dir, "FileRenamer.exe")
                if os.path.exists(app_exe):
                    print(f"Restarting app: {app_exe}")
                    subprocess.Popen([app_exe], start_new_session=True)
        else:
            print(f"Installer failed with exit code {result.returncode}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error during update: {e}")
        sys.exit(1)
    finally:
        # 4. Cleanup temp package if needed (optional as downloader does it)
        pass


if __name__ == "__main__":
    main()
