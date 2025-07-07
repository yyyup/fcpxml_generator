"""
FCPXML generation logic
Handles the creation of FCPXML files from cut data
"""

import os
import uuid
from typing import List, Dict, Tuple


class FCPXMLBuilder:
    """Builds FCPXML files from cut data"""
    
    def __init__(self):
        self.version = "1.10"
    
    def seconds_to_fcpxml_time(self, seconds: float, fps: float) -> str:
        """Convert seconds to FCPXML time format"""
        total_frames = int(round(seconds * fps))
        return f"{total_frames}/{int(fps)}s"
    
    def generate_single_fcpxml(self, cuts: List[Dict], video_path: str, fps: float, 
                              include_audio: bool = True, project_name: str = "Timeline") -> str:
        """Generate FCPXML content for a single video"""
        
        source_filename = os.path.basename(video_path)
        
        # Generate unique IDs
        asset_id = str(uuid.uuid4()).upper()
        project_id = str(uuid.uuid4()).upper()
        event_id = str(uuid.uuid4()).upper()
        
        # Calculate total timeline duration
        total_duration = sum(cut['end'] - cut['start'] for cut in cuts)
        total_duration_fcpxml = self.seconds_to_fcpxml_time(total_duration, fps)
        
        # Build audio attributes
        audio_attrs = 'hasAudio="1" audioSources="1" audioChannels="2"' if include_audio else ''
        
        # Start building FCPXML
        fcpxml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="{self.version}">
    <resources>
        <format id="r1" name="FFVideoFormat{int(fps)}p" frameDuration="1/{int(fps)}s" width="1920" height="1080" colorSpace="1-1-1 (Rec. 709)"/>
        <asset id="{asset_id}" name="{os.path.splitext(source_filename)[0]}" uid="{asset_id}" src="file://{video_path.replace(' ', '%20')}" start="0s" hasVideo="1" {audio_attrs} format="r1" duration="{self.seconds_to_fcpxml_time(9999, fps)}"/>
    </resources>
    <library>
        <event id="{event_id}" name="Auto Generated Timeline">
            <project id="{project_id}" name="{project_name}">
                <sequence format="r1" duration="{total_duration_fcpxml}">
                    <spine>'''
        
        # Add cuts to timeline
        timeline_position = 0
        for i, cut in enumerate(cuts):
            start_sec = cut['start']
            end_sec = cut['end']
            duration = end_sec - start_sec
            
            if duration <= 0:
                continue
            
            start_fcpxml = self.seconds_to_fcpxml_time(start_sec, fps)
            duration_fcpxml = self.seconds_to_fcpxml_time(duration, fps)
            offset_fcpxml = self.seconds_to_fcpxml_time(timeline_position, fps)
            
            clip_id = str(uuid.uuid4()).upper()
            
            fcpxml_content += f'''
                        <asset-clip id="{clip_id}" name="{source_filename}_cut_{i+1}" ref="{asset_id}" offset="{offset_fcpxml}" start="{start_fcpxml}" duration="{duration_fcpxml}"/>'''
            
            timeline_position += duration
        
        fcpxml_content += '''
                    </spine>
                </sequence>
            </project>
        </event>
    </library>
</fcpxml>'''
        
        return fcpxml_content
    
    def generate_multi_fcpxml(self, cuts: List[Dict], video_paths: List[str], fps: float, 
                             include_audio: bool = True) -> List[Tuple[str, str]]:
        """Generate multiple FCPXML files for multi-camera workflow"""
        
        results = []
        
        for video_path in video_paths:
            source_filename = os.path.basename(video_path)
            base_name = os.path.splitext(source_filename)[0]
            project_name = f"{base_name}_Timeline"
            
            fcpxml_content = self.generate_single_fcpxml(
                cuts, video_path, fps, include_audio, project_name
            )
            
            results.append((fcpxml_content, source_filename))
        
        return results
    
    def create_debug_info(self, cuts: List[Dict], video_paths: List[str], fps: float, 
                         include_audio: bool, is_multi_cam: bool) -> str:
        """Create debug information for troubleshooting"""
        
        debug_content = "=== FCPXML DEBUG INFO ===\n"
        debug_content += f"Mode: {'Multi-camera' if is_multi_cam else 'Single camera'}\n"
        debug_content += f"Number of Videos: {len(video_paths)}\n"
        debug_content += f"Include Audio: {include_audio}\n"
        debug_content += f"Number of Cuts: {len(cuts)}\n"
        debug_content += f"Frame Rate: {fps}\n"
        debug_content += f"Total Duration: {sum(cut['end'] - cut['start'] for cut in cuts):.1f} seconds\n"
        
        debug_content += "\n=== VIDEO SOURCES ===\n"
        for i, video_path in enumerate(video_paths, 1):
            debug_content += f"{i}. {os.path.basename(video_path)}\n"
        
        debug_content += "\n=== CUT LIST ===\n"
        for i, cut in enumerate(cuts, 1):
            duration = cut['end'] - cut['start']
            debug_content += f"Cut {i}: {cut['start']}s - {cut['end']}s ({duration:.1f}s)\n"
        
        return debug_content