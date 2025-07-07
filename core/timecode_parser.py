"""
Timecode parsing functionality
Handles extraction of timecodes from text files and JSON files
"""

import json
import re
from typing import List, Dict


class TimecodeParser:
    """Parses timecodes from various input formats"""
    
    def __init__(self):
        # Patterns for HH:MM:SS or MM:SS format ranges
        self.timecode_patterns = [
            r'(\d{1,2}:\d{2}:\d{2})[-–—](\d{1,2}:\d{2}:\d{2})',  # HH:MM:SS-HH:MM:SS
            r'(\d{1,2}:\d{2})[-–—](\d{1,2}:\d{2})',              # MM:SS-MM:SS
            r'(\d{1,2}:\d{2}:\d{2})\s*[-–—]\s*(\d{1,2}:\d{2}:\d{2})',  # with spaces
            r'(\d{1,2}:\d{2})\s*[-–—]\s*(\d{1,2}:\d{2})',        # MM:SS with spaces
        ]
    
    def load_from_json(self, file_path: str) -> List[Dict]:
        """Load cuts from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cuts = json.loads(content)
        
        # Validate JSON structure
        if not isinstance(cuts, list) or len(cuts) == 0:
            raise ValueError("JSON must be a list of cuts")
        
        if not all(key in cuts[0] for key in ['start', 'end']):
            raise ValueError("JSON cuts must have 'start' and 'end' fields")
        
        return cuts
    
    def load_from_text(self, file_path: str) -> List[Dict]:
        """Load cuts from text file by parsing timecodes"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_timecodes_from_text(content)
    
    def parse_timecodes_from_text(self, text: str) -> List[Dict]:
        """Extract timecodes from text content"""
        cuts = []
        
        for pattern in self.timecode_patterns:
            matches = re.findall(pattern, text)
            for start_tc, end_tc in matches:
                try:
                    start_seconds = self.timecode_to_seconds(start_tc)
                    end_seconds = self.timecode_to_seconds(end_tc)
                    if start_seconds < end_seconds:  # Valid range
                        cuts.append({"start": start_seconds, "end": end_seconds})
                except ValueError:
                    continue
        
        # Remove duplicates and sort
        cuts = list({(cut['start'], cut['end']): cut for cut in cuts}.values())
        cuts.sort(key=lambda x: x['start'])
        
        return cuts
    
    def timecode_to_seconds(self, timecode: str) -> float:
        """Convert timecode string to seconds"""
        parts = timecode.split(':')
        
        if len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:  # MM:SS
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        else:
            raise ValueError(f"Invalid timecode format: {timecode}")
    
    def seconds_to_display_timecode(self, seconds: float) -> str:
        """Convert seconds to MM:SS format for display"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def validate_cuts(self, cuts: List[Dict]) -> List[str]:
        """Validate cut list and return any warnings"""
        warnings = []
        
        if not cuts:
            warnings.append("No cuts found")
            return warnings
        
        for i, cut in enumerate(cuts, 1):
            # Check for required fields
            if 'start' not in cut or 'end' not in cut:
                warnings.append(f"Cut {i}: Missing 'start' or 'end' field")
                continue
            
            # Check for valid duration
            duration = cut['end'] - cut['start']
            if duration <= 0:
                warnings.append(f"Cut {i}: Invalid duration ({duration:.1f}s)")
            
            # Check for very short cuts
            if 0 < duration < 0.5:
                warnings.append(f"Cut {i}: Very short duration ({duration:.1f}s)")
        
        # Check for overlapping cuts
        sorted_cuts = sorted(cuts, key=lambda x: x['start'])
        for i in range(len(sorted_cuts) - 1):
            current_end = sorted_cuts[i]['end']
            next_start = sorted_cuts[i + 1]['start']
            if current_end > next_start:
                warnings.append(f"Cuts overlap: {current_end:.1f}s > {next_start:.1f}s")
        
        return warnings
    
    def get_total_duration(self, cuts: List[Dict]) -> float:
        """Calculate total duration of all cuts"""
        return sum(cut['end'] - cut['start'] for cut in cuts if cut['end'] > cut['start'])
    
    def format_cuts_summary(self, cuts: List[Dict]) -> str:
        """Create a formatted summary of cuts"""
        if not cuts:
            return "No cuts found"
        
        total_duration = self.get_total_duration(cuts)
        summary = f"Found {len(cuts)} cuts, total duration: {total_duration:.1f}s\n\n"
        
        for i, cut in enumerate(cuts, 1):
            duration = cut['end'] - cut['start']
            start_tc = self.seconds_to_display_timecode(cut['start'])
            end_tc = self.seconds_to_display_timecode(cut['end'])
            summary += f"Cut {i:2d}: {start_tc} - {end_tc} ({duration:.1f}s)\n"
        
        return summary