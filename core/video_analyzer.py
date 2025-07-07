"""
Video analysis functionality
Handles FPS detection and video file validation
"""

import subprocess
import json
import os
from typing import Optional, Dict, Any


class VideoAnalyzer:
    """Analyzes video files for metadata like frame rate"""
    
    def __init__(self):
        self.common_frame_rates = [23.976, 24, 25, 29.97, 30, 50, 59.94, 60]
    
    def detect_fps(self, video_path: str) -> Optional[str]:
        """
        Detect frame rate from video file using ffprobe
        Returns string representation of FPS or None if detection fails
        """
        try:
            return self._ffprobe_fps(video_path)
        except Exception:
            # If ffprobe fails, try alternative methods
            return self._fallback_fps_detection(video_path)
    
    def _ffprobe_fps(self, video_path: str) -> Optional[str]:
        """Use ffprobe to detect frame rate"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', '-select_streams', 'v:0', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return None
            
            info = json.loads(result.stdout)
            
            if not info.get('streams'):
                return None
            
            stream = info['streams'][0]
            
            # Try to get frame rate from various fields
            fps_candidates = []
            
            # r_frame_rate is usually the most accurate
            if 'r_frame_rate' in stream:
                fps = self._parse_fraction(stream['r_frame_rate'])
                if fps:
                    fps_candidates.append(fps)
            
            # avg_frame_rate as backup
            if 'avg_frame_rate' in stream:
                fps = self._parse_fraction(stream['avg_frame_rate'])
                if fps:
                    fps_candidates.append(fps)
            
            # Pick the best candidate
            for fps in fps_candidates:
                if 20 <= fps <= 120:  # Reasonable range
                    return self._round_to_common_fps(fps)
            
            return None
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, 
                json.JSONDecodeError, FileNotFoundError):
            return None
    
    def _parse_fraction(self, fraction_str: str) -> Optional[float]:
        """Parse fraction string like '30/1' or '30000/1001'"""
        try:
            if '/' in fraction_str:
                num, den = fraction_str.split('/')
                return float(num) / float(den)
            else:
                return float(fraction_str)
        except (ValueError, ZeroDivisionError):
            return None
    
    def _round_to_common_fps(self, fps: float) -> str:
        """Round detected FPS to common frame rates"""
        # Common frame rate mappings
        if 23.5 <= fps <= 24.5:
            return "24"
        elif 24.5 <= fps <= 25.5:
            return "25"
        elif 29.5 <= fps <= 30.5:
            return "30"
        elif 59.5 <= fps <= 60.5:
            return "60"
        else:
            # Round to nearest integer for uncommon rates
            return str(int(round(fps)))
    
    def _fallback_fps_detection(self, video_path: str) -> Optional[str]:
        """Fallback FPS detection methods when ffprobe is not available"""
        try:
            # Try to detect from filename patterns
            filename = os.path.basename(video_path).lower()
            
            # Common filename patterns
            if '24fps' in filename or '24p' in filename:
                return "24"
            elif '25fps' in filename or '25p' in filename:
                return "25"
            elif '30fps' in filename or '30p' in filename:
                return "30"
            elif '60fps' in filename or '60p' in filename:
                return "60"
            
            # Default fallback
            return "30"
            
        except Exception:
            return "30"  # Safe default
    
    def validate_video_file(self, video_path: str) -> Dict[str, Any]:
        """
        Validate video file and return information about it
        Returns dict with validation results and metadata
        """
        result = {
            'valid': False,
            'exists': False,
            'readable': False,
            'fps': None,
            'duration': None,
            'error': None
        }
        
        try:
            # Check if file exists
            if not os.path.exists(video_path):
                result['error'] = "File does not exist"
                return result
            
            result['exists'] = True
            
            # Check if file is readable
            if not os.access(video_path, os.R_OK):
                result['error'] = "File is not readable"
                return result
            
            result['readable'] = True
            
            # Try to detect FPS
            fps = self.detect_fps(video_path)
            if fps:
                result['fps'] = fps
            
            # Try to get duration (if ffprobe available)
            duration = self._get_video_duration(video_path)
            if duration:
                result['duration'] = duration
            
            result['valid'] = True
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _get_video_duration(self, video_path: str) -> Optional[float]:
        """Get video duration in seconds using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return None
            
            info = json.loads(result.stdout)
            
            if 'format' in info and 'duration' in info['format']:
                return float(info['format']['duration'])
            
            return None
            
        except Exception:
            return None
    
    def get_supported_formats(self) -> list:
        """Return list of supported video formats"""
        return [
            '.mp4', '.mov', '.avi', '.mkv', '.mxf', 
            '.prores', '.m4v', '.wmv', '.flv', '.webm'
        ]
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.get_supported_formats()
    
    def format_file_info(self, video_path: str) -> str:
        """Create formatted string with video file information"""
        validation = self.validate_video_file(video_path)
        
        info = f"File: {os.path.basename(video_path)}\n"
        info += f"Path: {video_path}\n"
        info += f"Exists: {'Yes' if validation['exists'] else 'No'}\n"
        info += f"Readable: {'Yes' if validation['readable'] else 'No'}\n"
        
        if validation['fps']:
            info += f"Frame Rate: {validation['fps']} fps\n"
        
        if validation['duration']:
            minutes = int(validation['duration'] // 60)
            seconds = int(validation['duration'] % 60)
            info += f"Duration: {minutes:02d}:{seconds:02d}\n"
        
        if validation['error']:
            info += f"Error: {validation['error']}\n"
        
        return info