"""
File management utilities
Handles file operations for saving FCPXML and debug files
"""

import os
from typing import List, Tuple


class FileManager:
    """Manages file operations for the application"""
    
    def __init__(self):
        self.supported_video_formats = [
            '.mp4', '.mov', '.avi', '.mkv', '.mxf', 
            '.prores', '.m4v', '.wmv', '.flv', '.webm'
        ]
    
    def save_single_fcpxml(self, fcpxml_content: str, reference_file: str, 
                          custom_filename: str = None) -> str:
        """
        Save a single FCPXML file
        Returns the path of the saved file
        """
        if custom_filename and custom_filename.strip():
            filename = custom_filename.strip()
            if not filename.lower().endswith('.fcpxml'):
                filename += '.fcpxml'
            fcpxml_path = os.path.join(os.path.dirname(reference_file), filename)
        else:
            base_name = os.path.splitext(reference_file)[0]
            fcpxml_path = f"{base_name}_timeline.fcpxml"
        
        with open(fcpxml_path, "w", encoding='utf-8') as f:
            f.write(fcpxml_content)
        
        return fcpxml_path
    
    def save_multiple_fcpxml(self, fcpxml_results: List[Tuple[str, str]], 
                           reference_file: str) -> List[str]:
        """
        Save multiple FCPXML files for multi-camera workflow
        Returns list of paths to saved files
        """
        saved_files = []
        
        for fcpxml_content, source_filename in fcpxml_results:
            # Generate filename based on source video
            base_name = os.path.splitext(source_filename)[0]
            fcpxml_filename = f"{base_name}_timeline.fcpxml"
            fcpxml_path = os.path.join(os.path.dirname(reference_file), fcpxml_filename)
            
            with open(fcpxml_path, "w", encoding='utf-8') as f:
                f.write(fcpxml_content)
            
            saved_files.append(fcpxml_path)
        
        return saved_files
    
    def save_debug_file(self, debug_content: str, reference_file: str) -> str:
        """
        Save debug information file
        Returns the path of the saved debug file
        """
        debug_path = f"{os.path.splitext(reference_file)[0]}_DEBUG.txt"
        
        with open(debug_path, "w", encoding='utf-8') as f:
            f.write(debug_content)
        
        return debug_path
    
    def validate_file_path(self, file_path: str) -> dict:
        """
        Validate a file path and return status information
        """
        result = {
            'valid': False,
            'exists': False,
            'readable': False,
            'writable': False,
            'error': None
        }
        
        try:
            # Check if file exists
            if os.path.exists(file_path):
                result['exists'] = True
                
                # Check if readable
                if os.access(file_path, os.R_OK):
                    result['readable'] = True
                
                # Check if directory is writable (for saving related files)
                directory = os.path.dirname(file_path)
                if os.access(directory, os.W_OK):
                    result['writable'] = True
            else:
                result['error'] = "File does not exist"
                return result
            
            result['valid'] = result['exists'] and result['readable'] and result['writable']
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def is_video_file(self, file_path: str) -> bool:
        """Check if file is a supported video format"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_video_formats
    
    def get_safe_filename(self, filename: str) -> str:
        """
        Clean filename to be safe for file systems
        Removes or replaces problematic characters
        """
        # Characters that are problematic in filenames
        unsafe_chars = '<>:"/\\|?*'
        
        safe_filename = filename
        for char in unsafe_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # Remove multiple consecutive underscores
        while '__' in safe_filename:
            safe_filename = safe_filename.replace('__', '_')
        
        # Remove leading/trailing underscores and spaces
        safe_filename = safe_filename.strip('_ ')
        
        return safe_filename
    
    def ensure_directory_exists(self, file_path: str) -> bool:
        """
        Ensure the directory for a file path exists
        Creates directories if they don't exist
        """
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            return True
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get comprehensive information about a file
        """
        info = {
            'path': file_path,
            'filename': os.path.basename(file_path),
            'directory': os.path.dirname(file_path),
            'extension': os.path.splitext(file_path)[1],
            'exists': False,
            'size': 0,
            'is_video': False,
            'error': None
        }
        
        try:
            if os.path.exists(file_path):
                info['exists'] = True
                info['size'] = os.path.getsize(file_path)
                info['is_video'] = self.is_video_file(file_path)
            else:
                info['error'] = "File does not exist"
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def cleanup_temp_files(self, directory: str, pattern: str = "*_temp*"):
        """
        Clean up temporary files in a directory
        """
        try:
            import glob
            temp_files = glob.glob(os.path.join(directory, pattern))
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except Exception:
                    pass  # Ignore errors when cleaning up
        except Exception:
            pass  # Ignore errors in cleanup
    
    def backup_file(self, file_path: str) -> str:
        """
        Create a backup of an existing file
        Returns path to backup file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Cannot backup non-existent file: {file_path}")
        
        # Generate backup filename
        base, ext = os.path.splitext(file_path)
        counter = 1
        backup_path = f"{base}_backup{ext}"
        
        while os.path.exists(backup_path):
            backup_path = f"{base}_backup_{counter}{ext}"
            counter += 1
        
        # Copy file to backup location
        import shutil
        shutil.copy2(file_path, backup_path)
        
        return backup_path
    
    def get_unique_filename(self, base_path: str) -> str:
        """
        Get a unique filename by appending numbers if file exists
        """
        if not os.path.exists(base_path):
            return base_path
        
        base, ext = os.path.splitext(base_path)
        counter = 1
        
        while True:
            new_path = f"{base}_{counter}{ext}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1