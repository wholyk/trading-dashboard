"""
Configuration management for ShortsFactory.
"""

import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class InboxConfig:
    """Inbox folder configuration"""
    long_videos: str = "INBOX/long_videos"
    clips: str = "INBOX/clips"
    ideas: str = "INBOX/ideas.txt"
    watch_interval: int = 5  # seconds


@dataclass
class StorageConfig:
    """Storage folder configuration"""
    originals: str = "storage/originals"
    intermediate: str = "storage/intermediate"
    finals: str = "storage/finals"
    captions: str = "storage/captions"
    metadata: str = "storage/metadata"


@dataclass
class VideoConfig:
    """Video processing configuration"""
    target_width: int = 1080
    target_height: int = 1920
    fps: int = 30
    max_duration: int = 60  # seconds
    min_duration: int = 15  # seconds
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    bitrate: str = "8M"


@dataclass
class CaptionConfig:
    """Caption configuration"""
    font_size: int = 48
    font_color: str = "white"
    bg_color: str = "black"
    bg_opacity: float = 0.7
    position: str = "bottom"
    max_words_per_line: int = 6


@dataclass
class UploadConfig:
    """Upload configuration"""
    enabled: bool = False  # Must be explicitly enabled
    min_delay_minutes: int = 60
    max_delay_minutes: int = 180
    max_per_day: int = 5
    privacy_status: str = "private"  # 'private', 'unlisted', 'public'
    category_id: str = "22"  # People & Blogs
    made_for_kids: bool = False


@dataclass
class WorkerConfig:
    """Worker configuration"""
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    timeout: int = 600  # seconds
    parallel_workers: int = 1


@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    host: str = "localhost"
    port: int = 8501
    title: str = "ShortsFactory Dashboard"


@dataclass
class Config:
    """Main configuration class"""
    inbox: InboxConfig = field(default_factory=InboxConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    video: VideoConfig = field(default_factory=VideoConfig)
    caption: CaptionConfig = field(default_factory=CaptionConfig)
    upload: UploadConfig = field(default_factory=UploadConfig)
    worker: WorkerConfig = field(default_factory=WorkerConfig)
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)
    
    database_path: str = "database/shortsfactory.db"
    log_dir: str = "logs"
    
    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        """Load configuration from YAML file"""
        if not os.path.exists(path):
            return cls()
        
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return cls()
        
        config = cls()
        
        # Update nested configs
        if 'inbox' in data:
            for key, value in data['inbox'].items():
                if hasattr(config.inbox, key):
                    setattr(config.inbox, key, value)
        
        if 'storage' in data:
            for key, value in data['storage'].items():
                if hasattr(config.storage, key):
                    setattr(config.storage, key, value)
        
        if 'video' in data:
            for key, value in data['video'].items():
                if hasattr(config.video, key):
                    setattr(config.video, key, value)
        
        if 'caption' in data:
            for key, value in data['caption'].items():
                if hasattr(config.caption, key):
                    setattr(config.caption, key, value)
        
        if 'upload' in data:
            for key, value in data['upload'].items():
                if hasattr(config.upload, key):
                    setattr(config.upload, key, value)
        
        if 'worker' in data:
            for key, value in data['worker'].items():
                if hasattr(config.worker, key):
                    setattr(config.worker, key, value)
        
        if 'dashboard' in data:
            for key, value in data['dashboard'].items():
                if hasattr(config.dashboard, key):
                    setattr(config.dashboard, key, value)
        
        # Update top-level configs
        if 'database_path' in data:
            config.database_path = data['database_path']
        if 'log_dir' in data:
            config.log_dir = data['log_dir']
        
        return config
    
    def to_yaml(self, path: str):
        """Save configuration to YAML file"""
        data = {
            'inbox': {
                'long_videos': self.inbox.long_videos,
                'clips': self.inbox.clips,
                'ideas': self.inbox.ideas,
                'watch_interval': self.inbox.watch_interval,
            },
            'storage': {
                'originals': self.storage.originals,
                'intermediate': self.storage.intermediate,
                'finals': self.storage.finals,
                'captions': self.storage.captions,
                'metadata': self.storage.metadata,
            },
            'video': {
                'target_width': self.video.target_width,
                'target_height': self.video.target_height,
                'fps': self.video.fps,
                'max_duration': self.video.max_duration,
                'min_duration': self.video.min_duration,
                'video_codec': self.video.video_codec,
                'audio_codec': self.video.audio_codec,
                'bitrate': self.video.bitrate,
            },
            'caption': {
                'font_size': self.caption.font_size,
                'font_color': self.caption.font_color,
                'bg_color': self.caption.bg_color,
                'bg_opacity': self.caption.bg_opacity,
                'position': self.caption.position,
                'max_words_per_line': self.caption.max_words_per_line,
            },
            'upload': {
                'enabled': self.upload.enabled,
                'min_delay_minutes': self.upload.min_delay_minutes,
                'max_delay_minutes': self.upload.max_delay_minutes,
                'max_per_day': self.upload.max_per_day,
                'privacy_status': self.upload.privacy_status,
                'category_id': self.upload.category_id,
                'made_for_kids': self.upload.made_for_kids,
            },
            'worker': {
                'max_retries': self.worker.max_retries,
                'retry_delay': self.worker.retry_delay,
                'timeout': self.worker.timeout,
                'parallel_workers': self.worker.parallel_workers,
            },
            'dashboard': {
                'host': self.dashboard.host,
                'port': self.dashboard.port,
                'title': self.dashboard.title,
            },
            'database_path': self.database_path,
            'log_dir': self.log_dir,
        }
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)


# Global configuration instance
_global_config = None


def get_config(config_path: str = "config/settings.yaml") -> Config:
    """Get or create global configuration instance"""
    global _global_config
    if _global_config is None:
        _global_config = Config.from_yaml(config_path)
    return _global_config


def save_default_config(config_path: str = "config/settings.yaml"):
    """Save default configuration to file"""
    config = Config()
    config.to_yaml(config_path)
