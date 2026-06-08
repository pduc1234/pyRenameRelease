"""Update package downloader logic."""
import os
import tempfile
import urllib.request
from typing import Optional, Callable


class UpdateDownloader:
    """Handles downloading update packages with progress reporting."""

    def __init__(self):
        self.temp_dir = os.path.join(tempfile.gettempdir(), "FileRenamerUpdate")
        os.makedirs(self.temp_dir, exist_ok=True)

    def download_package(self, url: str, progress_callback: Optional[Callable[[int], None]] = None) -> str:
        """
        Download update package (installer) to temp directory.
        
        Args:
            url: URL to download from.
            progress_callback: Optional function receiving percentage (0-100).
            
        Returns:
            Path to the downloaded file.
        """
        dest_path = os.path.join(self.temp_dir, "FileRenamer-Setup.exe")
        
        headers = {"User-Agent": "FileRenamer-App"}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            total_size = int(response.info().get('Content-Length', 0))
            downloaded = 0
            block_size = 8192
            
            with open(dest_path, "wb") as f:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    
                    downloaded += len(buffer)
                    f.write(buffer)
                    
                    if total_size > 0 and progress_callback:
                        percent = int(downloaded * 100 / total_size)
                        progress_callback(percent)
                        
        return dest_path

    def cleanup(self):
        """Delete downloaded files."""
        try:
            for f in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, f))
            os.rmdir(self.temp_dir)
        except Exception:
            pass
