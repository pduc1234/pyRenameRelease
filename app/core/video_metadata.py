"""Video metadata extraction."""
from typing import Optional


def get_resolution(path: str) -> Optional[str]:
    """
    Extract video resolution from file using pymediainfo.
    
    Returns:
        Resolution string like "1920x1080", or None if unable to detect
    """
    try:
        from pymediainfo import MediaInfo

        media_info = MediaInfo.parse(path)
        for track in media_info.tracks:
            if track.track_type == "Video":
                width = track.width
                height = track.height
                if width and height:
                    return f"{width}x{height}"
    except Exception:
        pass

    return None
