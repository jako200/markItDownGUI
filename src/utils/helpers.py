import os

SUPPORTED_EXTENSIONS = {
    ".docx": "Word Document",
    ".pptx": "PowerPoint Presentation",
    ".xlsx": "Excel Spreadsheet",
    ".pdf": "PDF File",
    ".html": "HTML Document",
    ".htm": "HTML Document",
    ".txt": "Text File",
    ".csv": "CSV Text File",
    ".xml": "XML File",
    ".json": "JSON File"
}

def format_size(size_bytes):
    """
    Format bytes to a human readable string.
    """
    if size_bytes is None or size_bytes < 0:
        return "N/A"
    if size_bytes == 0:
        return "0 B"
    
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(os.sys.float_info.max)
    # math.log(size_bytes, 1024)
    # Using simple division to avoid imports if possible, or just standard math
    import math
    if size_bytes == 0:
        return "0 B"
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def get_file_extension(path):
    """
    Returns the file extension in lowercase, e.g. '.docx'
    """
    _, ext = os.path.splitext(path)
    return ext.lower()

def is_supported_file(path):
    """
    Returns True if the file extension is supported by MarkItDown.
    """
    ext = get_file_extension(path)
    return ext in SUPPORTED_EXTENSIONS

def get_file_type_description(path):
    """
    Returns a brief description of the file type.
    """
    ext = get_file_extension(path)
    return SUPPORTED_EXTENSIONS.get(ext, "Unknown File")
