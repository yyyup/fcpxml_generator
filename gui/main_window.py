"""
Main GUI window for FCPXML Generator
Handles all user interface components and interactions
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import traceback
import os

from core.fcpxml_generator import FCPXMLBuilder
from core.timecode_parser import TimecodeParser
from core.video_analyzer import VideoAnalyzer
from utils.file_helpers import FileManager


class FCPXMLGeneratorApp:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FCPXML Generator for DaVinci Resolve")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Initialize components
        self.fcpxml_builder = FCPXMLBuilder()
        self.parser = TimecodeParser()
        self.video_analyzer = VideoAnalyzer()
        self.file_manager = FileManager()
        
        # Initialize variables
        self._init_variables()
        
        # Setup UI
        self.setup_ui()
        
    def _init_variables(self):
        """Initialize all tkinter variables"""
        self.input_file = None
        self.fps = tk.StringVar(value="30")
        self.auto_fps = tk.BooleanVar(value=True)
        self.detected_fps = None
        self.source_video_path = tk.StringVar(value="")
        self.fcpxml_filename = tk.StringVar(value="")
        self.input_type = tk.StringVar(value="json")
        self.include_audio = tk.BooleanVar(value=True)
        self.multi_video_mode = tk.BooleanVar(value=False)
        self.video_files = []
        self.cuts_data = []
        self.status_label = None
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Create scrollable frame
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main frame with padding
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Build UI sections
        self._create_header(main_frame)
        self._create_input_selection(main_frame)
        self._create_file_selection(main_frame)
        self._create_video_selection(main_frame)
        self._create_audio_options(main_frame)
        self._create_fps_options(main_frame)
        self._create_output_options(main_frame)
        self._create_reorder_section(main_frame)
        self._create_action_buttons(main_frame)
        self._create_status_section(main_frame)
        
        # Configure scrolling
        self._setup_scrolling(canvas)
    
    def _create_header(self, parent):
        """Create header section"""
        # Title
        title_label = ttk.Label(parent, text="FCPXML Generator for DaVinci Resolve", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = """This tool converts cut lists into FCPXML files for DaVinci Resolve.
No more reel name confusion - uses direct file references!"""
        
        instructions_label = ttk.Label(parent, text=instructions, 
                                     justify=tk.LEFT, wraplength=500)
        instructions_label.pack(pady=(0, 20))
    
    def _create_input_selection(self, parent):
        """Create input type selection"""
        step1_frame = ttk.LabelFrame(parent, text="Step 1: Choose Input Type", padding="10")
        step1_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Radiobutton(step1_frame, text="JSON file", 
                       variable=self.input_type, value="json").pack(anchor="w")
        ttk.Radiobutton(step1_frame, text="Text file with timecodes", 
                       variable=self.input_type, value="text").pack(anchor="w")
    
    def _create_file_selection(self, parent):
        """Create cut list file selection"""
        step2_frame = ttk.LabelFrame(parent, text="Step 2: Select Your Cut List", padding="10")
        step2_frame.pack(fill="x", pady=(0, 10))
        
        cuts_file_frame = ttk.Frame(step2_frame)
        cuts_file_frame.pack(fill="x")
        
        self.cuts_file_label = ttk.Label(cuts_file_frame, text="No file selected", foreground="gray")
        self.cuts_file_label.pack(side="left", fill="x", expand=True)
        
        select_cuts_button = ttk.Button(cuts_file_frame, text="Browse Cut List", command=self.select_cuts_file)
        select_cuts_button.pack(side="right")
    
    def _create_video_selection(self, parent):
        """Create video selection section"""
        step3_frame = ttk.LabelFrame(parent, text="Step 3: Select Source Video(s)", padding="10")
        step3_frame.pack(fill="x", pady=(0, 10))
        
        # Multi-video option
        multi_check = ttk.Checkbutton(step3_frame, text="Multi-camera mode (same cuts, multiple videos)", 
                                    variable=self.multi_video_mode, command=self.toggle_multi_mode)
        multi_check.pack(anchor="w", pady=(0, 10))
        
        # Single video frame
        self.single_video_frame = ttk.Frame(step3_frame)
        self.single_video_frame.pack(fill="x")
        
        single_file_frame = ttk.Frame(self.single_video_frame)
        single_file_frame.pack(fill="x")
        
        self.video_file_label = ttk.Label(single_file_frame, text="No video file selected", foreground="gray")
        self.video_file_label.pack(side="left", fill="x", expand=True)
        
        select_video_button = ttk.Button(single_file_frame, text="Browse Video File", command=self.select_video_file)
        select_video_button.pack(side="right")
        
        # Multi video frame
        self.multi_video_frame = ttk.Frame(step3_frame)
        
        multi_label = ttk.Label(self.multi_video_frame, text="Select multiple video files (same cuts will be applied to all):")
        multi_label.pack(anchor="w", pady=(0, 5))
        
        multi_buttons_frame = ttk.Frame(self.multi_video_frame)
        multi_buttons_frame.pack(fill="x")
        
        add_video_button = ttk.Button(multi_buttons_frame, text="Add Video File", command=self.add_video_file)
        add_video_button.pack(side="left", padx=(0, 10))
        
        clear_videos_button = ttk.Button(multi_buttons_frame, text="Clear All", command=self.clear_video_files)
        clear_videos_button.pack(side="left")
        
        # Video list
        self.video_list_frame = ttk.Frame(self.multi_video_frame)
        self.video_list_frame.pack(fill="x", pady=(10, 0))
        
        help_label = ttk.Label(step3_frame, text="💡 Multi-camera mode creates separate FCPXML files with identical cuts!", 
                              foreground="blue", font=("Arial", 9))
        help_label.pack(anchor="w", pady=(10, 0))
        
        # Initialize mode
        self.toggle_multi_mode()
    
    def _create_audio_options(self, parent):
        """Create audio options section"""
        step4_frame = ttk.LabelFrame(parent, text="Step 4: Audio Options", padding="10")
        step4_frame.pack(fill="x", pady=(0, 10))
        
        audio_check = ttk.Checkbutton(step4_frame, text="Include audio from source video", 
                                    variable=self.include_audio)
        audio_check.pack(anchor="w")
        
        help_label_audio = ttk.Label(step4_frame, text="💡 Most videos have embedded audio that will be included", 
                                   foreground="blue", font=("Arial", 9))
        help_label_audio.pack(anchor="w", pady=(5, 0))
    
    def _create_fps_options(self, parent):
        """Create frame rate options section"""
        step5_frame = ttk.LabelFrame(parent, text="Step 5: Video Frame Rate", padding="10")
        step5_frame.pack(fill="x", pady=(0, 10))
        
        # Auto-detect frame rate option
        auto_fps_check = ttk.Checkbutton(step5_frame, text="Auto-detect frame rate from video", 
                                       variable=self.auto_fps, command=self.toggle_fps_mode)
        auto_fps_check.pack(anchor="w", pady=(0, 10))
        
        # Manual FPS selection frame
        self.manual_fps_frame = ttk.Frame(step5_frame)
        self.manual_fps_frame.pack(anchor="w")
        
        fps_label = ttk.Label(self.manual_fps_frame, text="Manual frame rate selection:")
        fps_label.pack(anchor="w", pady=(0, 5))
        
        fps_options_frame = ttk.Frame(self.manual_fps_frame)
        fps_options_frame.pack(anchor="w")
        
        fps_options = [("24 fps", "24"), ("25 fps", "25"), ("30 fps", "30"), ("60 fps", "60")]
        
        for i, (text, value) in enumerate(fps_options):
            rb = ttk.Radiobutton(fps_options_frame, text=text, variable=self.fps, value=value)
            rb.grid(row=i//2, column=i%2, sticky="w", padx=(0, 20), pady=2)
        
        # FPS detection status
        self.fps_status_label = ttk.Label(step5_frame, text="", foreground="blue", font=("Arial", 9))
        self.fps_status_label.pack(anchor="w", pady=(10, 0))
        
        # Initialize FPS mode
        self.toggle_fps_mode()
    
    def _create_output_options(self, parent):
        """Create output filename options"""
        step6_frame = ttk.LabelFrame(parent, text="Step 6: Output Filename (Optional)", padding="10")
        step6_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(step6_frame, text="FCPXML filename:").pack(anchor="w")
        fcpxml_entry = ttk.Entry(step6_frame, textvariable=self.fcpxml_filename)
        fcpxml_entry.pack(fill="x", pady=(5, 0))
        
        help_label2 = ttk.Label(step6_frame, text="💡 Leave blank to auto-generate", 
                               foreground="blue", font=("Arial", 9))
        help_label2.pack(anchor="w", pady=(5, 0))
    
    def _create_reorder_section(self, parent):
        """Create cut reordering section"""
        step7_frame = ttk.LabelFrame(parent, text="Step 7: Reorder Cuts (Optional)", padding="10")
        step7_frame.pack(fill="x", pady=(0, 10))
        
        self.reorder_button = ttk.Button(step7_frame, text="Preview & Reorder Cuts", 
                                       command=self.show_reorder_window, state="disabled")
        self.reorder_button.pack(anchor="w")
    
    def _create_action_buttons(self, parent):
        """Create main action buttons"""
        generate_button = ttk.Button(parent, text="Generate FCPXML File", command=self.generate_fcpxml)
        generate_button.pack(pady=(20, 10))
    
    def _create_status_section(self, parent):
        """Create status display section"""
        self.status_label = ttk.Label(parent, text="Ready to generate FCPXML", foreground="green")
        self.status_label.pack(pady=(10, 20))
    
    def _setup_scrolling(self, canvas):
        """Setup mousewheel scrolling"""
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Event handlers and business logic
    def toggle_multi_mode(self):
        """Toggle between single and multi-video modes"""
        if self.multi_video_mode.get():
            self.single_video_frame.pack_forget()
            self.multi_video_frame.pack(fill="x")
        else:
            self.multi_video_frame.pack_forget()
            self.single_video_frame.pack(fill="x")
        self.update_status()
    
    def toggle_fps_mode(self):
        """Toggle between auto-detect and manual FPS selection"""
        if self.auto_fps.get():
            self.manual_fps_frame.pack_forget()
            self.fps_status_label.config(text="💡 Frame rate will be detected from first video file")
        else:
            self.manual_fps_frame.pack(anchor="w")
            self.fps_status_label.config(text="💡 Using manually selected frame rate")
    
    def select_cuts_file(self):
        """Handle cut list file selection"""
        if self.input_type.get() == "json":
            filetypes = [("JSON files", "*.json"), ("All files", "*.*")]
        else:
            filetypes = [("Text files", "*.txt"), ("All files", "*.*")]
        
        file_path = filedialog.askopenfilename(
            title="Select your cut list file",
            filetypes=filetypes
        )
        
        if file_path:
            self.input_file = file_path
            filename = os.path.basename(file_path)
            self.cuts_file_label.config(text=f"Selected: {filename}", foreground="black")
            
            # Try to load cuts and enable reorder button
            try:
                self.cuts_data = self.load_cuts_data()
                self.reorder_button.config(state="normal")
                self.update_status()
            except Exception as e:
                self.status_label.config(text=f"Error loading cuts: {str(e)}", foreground="red")
            
            # Auto-fill FCPXML filename if not set
            if not self.fcpxml_filename.get():
                base_name = os.path.splitext(filename)[0]
                self.fcpxml_filename.set(f"{base_name}_timeline")
    
    def select_video_file(self):
        """Handle single video file selection"""
        filetypes = [
            ("Video files", "*.mp4 *.mov *.avi *.mkv *.mxf *.prores *.m4v"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select your source video file",
            filetypes=filetypes
        )
        
        if file_path:
            self.source_video_path.set(file_path)
            filename = os.path.basename(file_path)
            self.video_file_label.config(text=f"Selected: {filename}", foreground="black")
            
            # Auto-detect FPS if enabled
            self.update_fps_from_video(file_path)
            self.update_status()
    
    def add_video_file(self):
        """Add a video file to the multi-video list"""
        filetypes = [
            ("Video files", "*.mp4 *.mov *.avi *.mkv *.mxf *.prores *.m4v"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select video file to add",
            filetypes=filetypes
        )
        
        if file_path and file_path not in self.video_files:
            self.video_files.append(file_path)
            
            # Auto-detect FPS from first video if enabled
            if len(self.video_files) == 1:
                self.update_fps_from_video(file_path)
            
            self.refresh_video_list()
            self.update_status()
    
    def clear_video_files(self):
        """Clear all video files"""
        self.video_files = []
        self.refresh_video_list()
        self.update_status()
    
    def remove_video_file(self, file_path):
        """Remove a specific video file"""
        if file_path in self.video_files:
            self.video_files.remove(file_path)
            self.refresh_video_list()
            self.update_status()
    
    def refresh_video_list(self):
        """Refresh the display of video files"""
        # Clear existing widgets
        for widget in self.video_list_frame.winfo_children():
            widget.destroy()
        
        if not self.video_files:
            no_files_label = ttk.Label(self.video_list_frame, text="No video files added", foreground="gray")
            no_files_label.pack(anchor="w")
        else:
            for i, file_path in enumerate(self.video_files, 1):
                file_frame = ttk.Frame(self.video_list_frame)
                file_frame.pack(fill="x", pady=2)
                
                filename = os.path.basename(file_path)
                file_label = ttk.Label(file_frame, text=f"{i}. {filename}")
                file_label.pack(side="left", fill="x", expand=True)
                
                remove_button = ttk.Button(file_frame, text="Remove", 
                                         command=lambda fp=file_path: self.remove_video_file(fp))
                remove_button.pack(side="right")
    
    def update_fps_from_video(self, video_path):
        """Update FPS based on video file"""
        if self.auto_fps.get():
            detected_fps = self.video_analyzer.detect_fps(video_path)
            if detected_fps:
                self.detected_fps = detected_fps
                self.fps_status_label.config(text=f"✅ Detected: {detected_fps} fps from video", foreground="green")
            else:
                self.detected_fps = "30"  # fallback
                self.fps_status_label.config(text="⚠️ Could not detect FPS, using 30 fps default", foreground="orange")
    
    def get_effective_fps(self):
        """Get the effective FPS to use for generation"""
        if self.auto_fps.get() and self.detected_fps:
            return float(self.detected_fps)
        else:
            return float(self.fps.get())
    
    def update_status(self):
        """Update status based on current selections"""
        if not self.status_label:
            return
            
        has_cuts = bool(self.cuts_data)
        
        if self.multi_video_mode.get():
            has_videos = bool(self.video_files)
            if has_cuts and has_videos:
                self.status_label.config(text=f"Ready! Will generate {len(self.video_files)} FCPXML files.", foreground="green")
            elif has_cuts:
                self.status_label.config(text="Add video files to generate FCPXML.", foreground="orange")
            elif has_videos:
                self.status_label.config(text="Select cut list file first.", foreground="orange")
            else:
                self.status_label.config(text="Select cut list and add video files.", foreground="orange")
        else:
            has_video = bool(self.source_video_path.get())
            if has_cuts and has_video:
                self.status_label.config(text="Ready to generate FCPXML!", foreground="green")
            elif has_cuts:
                self.status_label.config(text="Select video file next.", foreground="orange")
            elif has_video:
                self.status_label.config(text="Select cut list file first.", foreground="orange")
            else:
                self.status_label.config(text="Ready to generate FCPXML", foreground="green")
    
    def load_cuts_data(self):
        """Load cuts data from file"""
        if self.input_type.get() == "json":
            return self.parser.load_from_json(self.input_file)
        else:
            return self.parser.load_from_text(self.input_file)
    
    def show_reorder_window(self):
        """Show cut reordering window"""
        if not self.cuts_data:
            return
            
        reorder_window = tk.Toplevel(self.root)
        reorder_window.title("Reorder Cuts")
        reorder_window.geometry("500x400")
        
        # Instructions
        ttk.Label(reorder_window, text="Use buttons to reorder cuts:", 
                 font=("Arial", 12)).pack(pady=10)
        
        # Listbox frame
        list_frame = ttk.Frame(reorder_window)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Listbox with scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.cuts_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.cuts_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.cuts_listbox.yview)
        
        # Populate listbox
        self.refresh_cuts_list()
        
        # Buttons
        button_frame = ttk.Frame(reorder_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Move Up", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Move Down", command=self.move_down).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Reset Order", command=self.reset_order).pack(side="left", padx=10)
        
        # Close button
        ttk.Button(reorder_window, text="Apply & Close", 
                  command=lambda: self.close_reorder_window(reorder_window)).pack(pady=10)
        
        # Store original order
        self.original_cuts = self.cuts_data.copy()
    
    def refresh_cuts_list(self):
        """Refresh the cuts display"""
        self.cuts_listbox.delete(0, tk.END)
        for i, cut in enumerate(self.cuts_data, 1):
            duration = cut['end'] - cut['start']
            start_tc = self.parser.seconds_to_display_timecode(cut['start'])
            end_tc = self.parser.seconds_to_display_timecode(cut['end'])
            display = f"{i:2d}. {start_tc} - {end_tc} ({duration:.1f}s)"
            self.cuts_listbox.insert(tk.END, display)
    
    def move_up(self):
        """Move selected cut up"""
        selection = self.cuts_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        idx = selection[0]
        self.cuts_data[idx], self.cuts_data[idx-1] = self.cuts_data[idx-1], self.cuts_data[idx]
        self.refresh_cuts_list()
        self.cuts_listbox.selection_set(idx-1)
    
    def move_down(self):
        """Move selected cut down"""
        selection = self.cuts_listbox.curselection()
        if not selection or selection[0] == len(self.cuts_data) - 1:
            return
        
        idx = selection[0]
        self.cuts_data[idx], self.cuts_data[idx+1] = self.cuts_data[idx+1], self.cuts_data[idx]
        self.refresh_cuts_list()
        self.cuts_listbox.selection_set(idx+1)
    
    def reset_order(self):
        """Reset to original order"""
        if hasattr(self, 'original_cuts'):
            self.cuts_data = self.original_cuts.copy()
            self.refresh_cuts_list()
    
    def close_reorder_window(self, window):
        """Close reorder window and update status"""
        window.destroy()
        self.status_label.config(text=f"Cuts reordered! {len(self.cuts_data)} cuts ready.", foreground="green")
    
    def generate_fcpxml(self):
        """Generate the FCPXML file(s)"""
        if not self.input_file:
            messagebox.showerror("Error", "Please select a cut list file first.")
            return
        
        # Validate video selection based on mode
        if self.multi_video_mode.get():
            if not self.video_files:
                messagebox.showerror("Error", "Please add at least one video file.")
                return
            video_sources = self.video_files
        else:
            if not self.source_video_path.get().strip():
                messagebox.showerror("Error", "Please select a source video file.")
                return
            video_sources = [self.source_video_path.get()]
        
        try:
            # Use reordered cuts if available, otherwise load fresh
            if self.cuts_data:
                cuts = self.cuts_data
            else:
                cuts = self.load_cuts_data()
            
            fps = self.get_effective_fps()
            is_multi_cam = self.multi_video_mode.get()
            
            # Generate FCPXML files
            if is_multi_cam:
                results = self.fcpxml_builder.generate_multi_fcpxml(
                    cuts, video_sources, fps, self.include_audio.get()
                )
                generated_files = self.file_manager.save_multiple_fcpxml(
                    results, self.input_file
                )
            else:
                fcpxml_content = self.fcpxml_builder.generate_single_fcpxml(
                    cuts, video_sources[0], fps, self.include_audio.get(),
                    self.fcpxml_filename.get() or 'Timeline'
                )
                generated_files = [self.file_manager.save_single_fcpxml(
                    fcpxml_content, self.input_file, self.fcpxml_filename.get()
                )]
            
            # Create debug file
            debug_content = self.fcpxml_builder.create_debug_info(
                cuts, video_sources, fps, self.include_audio.get(), is_multi_cam
            )
            debug_path = self.file_manager.save_debug_file(debug_content, self.input_file)
            
            # Show success message
            self.show_success_message(generated_files, debug_path, cuts, is_multi_cam)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating FCPXML: {str(e)}")
            print(f"Full error: {traceback.format_exc()}")
    
    def show_success_message(self, generated_files, debug_path, cuts, is_multi_cam):
        """Show success message with appropriate details"""
        audio_info = "with audio" if self.include_audio.get() else "video only"
        
        if is_multi_cam:
            file_list = "\n".join([f"• {os.path.basename(path)}" for path in generated_files])
            success_message = f"""✅ Multi-camera FCPXML files generated successfully!

Generated {len(generated_files)} files:
{file_list}

Debug file: {os.path.basename(debug_path)}
Cuts: {len(cuts)} ({audio_info})

DaVinci Resolve workflow:
1. File → Import → Timeline (repeat for each FCPXML)
2. You'll get {len(generated_files)} separate timelines
3. All timelines have IDENTICAL cuts and timing
4. Copy/paste clips between timelines to create your final edit
5. Perfect multi-camera sync achieved!

💡 This bypasses FCPXML's multi-track limitations perfectly!"""
        else:
            success_message = f"""✅ FCPXML generated successfully!

Location: {os.path.basename(generated_files[0])}
Debug file: {os.path.basename(debug_path)}
Cuts: {len(cuts)} ({audio_info})

DaVinci Resolve steps:
1. File → Import → Timeline
2. Select the FCPXML file
3. Timeline will be created with exact file references!

💡 FCPXML includes {"both video and audio tracks" if self.include_audio.get() else "video track only"}."""
        
        messagebox.showinfo("Success!", success_message)
        self.status_label.config(text=f"Generated {len(generated_files)} FCPXML file(s) successfully!", foreground="green")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()