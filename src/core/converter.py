import os
import threading
import sys

# Try importing MarkItDown
try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False

class MarkdownConverter:
    """
    Handles single document conversions using the MarkItDown API.
    """
    def __init__(self):
        self.md_engine = None
        self.init_error = None
        if MARKITDOWN_AVAILABLE:
            try:
                self.md_engine = MarkItDown()
            except Exception as e:
                import traceback
                self.init_error = traceback.format_exc()
                # Catch any issues with internal sub-engines initialization
                pass

    def is_available(self):
        """Returns True if the markitdown library is loaded and initialized."""
        return MARKITDOWN_AVAILABLE and self.md_engine is not None

    def convert(self, input_path, output_path):
        """
        Converts the input file to Markdown and writes it to the output path.
        Throws exceptions on failures.
        """
        if not self.is_available():
            raise RuntimeError("Microsoft MarkItDown is not installed or did not initialize correctly.")
            
        input_path = os.path.abspath(input_path)
        output_path = os.path.abspath(output_path)
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"File di input non trovato: {input_path}")
            
        # Run conversion
        result = self.md_engine.convert(input_path)
        
        # Ensure parent directory of output exists
        out_dir = os.path.dirname(output_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
            
        # Write file UTF-8
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.text_content)
            
        return output_path


class BatchConversionWorker:
    """
    Manages sequential batch conversions in a background thread.
    Can be cooperative-cancelled from the GUI.
    """
    def __init__(self, converter, files, output_dir=None, callbacks=None):
        """
        files: List of filepaths to convert.
        output_dir: If set, all outputs go to this directory. If None,
                    each output goes to the respective source file directory.
        callbacks: Dict containing callback functions:
                   - on_file_start(filepath)
                   - on_file_success(filepath, output_path)
                   - on_file_error(filepath, error_msg)
                   - on_progress(converted_num, total_num)
                   - on_complete(success_num, error_num)
        """
        self.converter = converter
        self.files = files
        self.output_dir = output_dir
        self.callbacks = callbacks or {}
        
        self.is_cancelled = False
        self.thread = None

    def start(self):
        """Starts the background thread worker."""
        self.is_cancelled = False
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def cancel(self):
        """Sets cancellation flag to stop processing remaining files."""
        self.is_cancelled = True

    def _run(self):
        total_files = len(self.files)
        success_count = 0
        error_count = 0
        
        for idx, filepath in enumerate(self.files):
            if self.is_cancelled:
                break
                
            # Trigger start callback
            if "on_file_start" in self.callbacks:
                self.callbacks["on_file_start"](filepath)
                
            # Determine output path
            try:
                dir_name, file_name = os.path.split(filepath)
                base_name, _ = os.path.splitext(file_name)
                
                target_dir = self.output_dir if self.output_dir else dir_name
                output_path = os.path.join(target_dir, f"{base_name}.md")
                
                # Execute conversion
                self.converter.convert(filepath, output_path)
                
                success_count += 1
                if "on_file_success" in self.callbacks:
                    self.callbacks["on_file_success"](filepath, output_path)
                    
            except Exception as e:
                error_count += 1
                if "on_file_error" in self.callbacks:
                    self.callbacks["on_file_error"](filepath, str(e))
            
            # Progress callback
            if "on_progress" in self.callbacks:
                self.callbacks["on_progress"](idx + 1, total_files)
                
        # Final callback
        if "on_complete" in self.callbacks:
            self.callbacks["on_complete"](success_count, error_count, self.is_cancelled)
