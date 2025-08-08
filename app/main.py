from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import markdown
import os
from typing import Optional

app = FastAPI(
    title="Markdown to HTML Converter API",
    description="Convert Markdown content to styled HTML with various modern themes",
    version="1.0.0"
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class MarkdownRequest(BaseModel):
    markdown_content: str
    theme: str = "mocha-minimalist"

class ConversionResponse(BaseModel):
    html_content: str
    theme_used: str
    success: bool
    message: str

# Available themes
AVAILABLE_THEMES = [
    "mocha-minimalist",
    "neon-brutalist", 
    "glassmorphism-pro",
    "sunset-gradient",
    "dark-sage",
    "corporate-blue",
    "retro-tech"
]

def _is_list_item(line: str) -> tuple[bool, str]:
    """Check if a line is a list item and return (is_list, type).
    
    Returns:
        tuple: (is_list_item, list_type) where list_type is 'unordered', 'ordered', or 'none'
    """
    stripped = line.lstrip()
    
    # Check unordered list markers
    if stripped.startswith(('- ', '* ', '+ ')):
        return True, 'unordered'
    
    # Check ordered list markers (number followed by dot and space)
    if len(stripped) > 2:
        parts = stripped.split('. ', 1)
        if len(parts) == 2 and parts[0].isdigit():
            return True, 'ordered'
    
    return False, 'none'


def _is_citation_line(line: str) -> bool:
    """Check if a line is a citation in [n] format."""
    stripped = line.strip()
    return (stripped.startswith('[') and 
            ']' in stripped and 
            stripped.find(']') > 1 and
            stripped[1:stripped.find(']')].isdigit())


def _fix_list_indentation(line: str) -> str:
    """Convert 2-space indentation to 4-space for proper Markdown nesting."""
    is_list, _ = _is_list_item(line)
    if not is_list:
        return line
    
    indent = len(line) - len(line.lstrip())
    if 0 < indent < 4:  # If indented but not enough for proper nesting
        return '    ' + line.lstrip()
    
    return line


def _process_special_sections(lines: list[str]) -> list[str]:
    """Process special sections like citations that need custom formatting."""
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Detect section headers that need special processing
        if line.strip().lower().endswith(':') and line.strip().lower() in ['citations:', 'references:', 'bibliography:']:
            # Add an explicit line break after the caption so the content starts on the next line
            result.append(line.rstrip() + '<br>')
            i += 1
            
            # Process the section content
            while i < len(lines):
                current_line = lines[i]
                
                # End of section: empty line followed by non-citation content
                if (not current_line.strip() and 
                    i + 1 < len(lines) and 
                    lines[i + 1].strip() and 
                    not _is_citation_line(lines[i + 1])):
                    result.append(current_line)
                    break
                
                # End of section: non-citation, non-empty line
                if current_line.strip() and not _is_citation_line(current_line):
                    # This line belongs to the next section, don't consume it
                    break
                
                # Process citation lines
                if _is_citation_line(current_line):
                    # Add line break formatting for proper display
                    result.append(current_line.rstrip() + '  ')
                else:
                    result.append(current_line)
                
                i += 1
            continue
        
        result.append(line)
        i += 1
    
    return result


def _is_header(line: str) -> bool:
    """Check if a line is a Markdown header."""
    stripped = line.strip()
    return stripped.startswith('#') and ' ' in stripped


def _clean_blank_lines(lines: list[str]) -> list[str]:
    """Remove excessive blank lines and ensure proper spacing around lists."""
    result = []
    prev_blank = False
    in_list_block = False  # Track if we're inside a list block (including nested items)
    prev_is_header = False
    
    for i, line in enumerate(lines):
        # Clean trailing whitespace from blank lines to prevent <p> wrapping
        cleaned_line = line.rstrip() if line.strip() == '' else line
        is_blank = not cleaned_line.strip()
        is_list, _ = _is_list_item(cleaned_line)
        is_nested = len(cleaned_line) > len(cleaned_line.lstrip()) and len(cleaned_line.lstrip()) > 0
        is_header = _is_header(cleaned_line)
        is_top_level_list = is_list and not is_nested
        
        # Check if next line is also a top-level list item
        next_is_top_level_list = False
        if i + 1 < len(lines):
            next_line_cleaned = lines[i + 1].rstrip() if lines[i + 1].strip() == '' else lines[i + 1]
            next_is_list, _ = _is_list_item(next_line_cleaned)
            next_is_nested = len(next_line_cleaned) > len(next_line_cleaned.lstrip()) and len(next_line_cleaned.lstrip()) > 0
            next_is_top_level_list = next_is_list and not next_is_nested
        
        # Skip consecutive blank lines
        if is_blank and prev_blank:
            continue
        
        # Skip blank lines between top-level list items to prevent <p> wrapping
        if (is_blank and in_list_block and next_is_top_level_list):
            continue
        
        # Add blank line before top-level list items that follow non-list content
        # BUT NOT if the previous line was a header (to avoid <p> wrapping)
        if (is_top_level_list and not in_list_block and 
            not prev_blank and not prev_is_header and i > 0 and result):
            result.append('')
        
        # Skip blank lines between list items and their nested content
        if (is_blank and in_list_block and 
            i + 1 < len(lines) and 
            len(lines[i + 1]) > len(lines[i + 1].lstrip())):
            continue
        
        # Use cleaned line (removes trailing spaces from blank lines)
        result.append(cleaned_line)
        prev_blank = is_blank
        
        # Update state tracking
        if not is_blank:
            if is_top_level_list:
                in_list_block = True  # Start or continue list block
            elif not is_list and not is_nested:
                in_list_block = False  # End list block when we hit non-list content
            prev_is_header = is_header
    
    return result


def preprocess_markdown_for_nested_lists(markdown_content: str) -> str:
    """Preprocess Markdown content to fix common formatting issues.
    
    This function applies several transformations to ensure proper Markdown parsing:
    1. Fixes list indentation (converts 2-space to 4-space for nesting)
    2. Handles special sections like citations with custom formatting
    3. Cleans up excessive blank lines while preserving structure
    
    Args:
        markdown_content: Raw Markdown content string
        
    Returns:
        Processed Markdown content with formatting fixes applied
    """
    if not markdown_content.strip():
        return markdown_content
    
    lines = markdown_content.split('\n')
    
    # Apply transformations in sequence
    lines = [_fix_list_indentation(line) for line in lines]
    lines = _process_special_sections(lines)
    lines = _clean_blank_lines(lines)
    
    # Ensure proper ending
    result = '\n'.join(lines)
    if result and not result.endswith('\n'):
        result += '\n'
    
    return result

def load_theme_css(theme_name: str) -> str:
    """Load CSS content for the specified theme"""
    theme_file = f"themes/{theme_name}.css"
    if os.path.exists(theme_file):
        with open(theme_file, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Return default theme if requested theme not found
        with open("themes/mocha-minimalist.css", 'r', encoding='utf-8') as f:
            return f.read()

def convert_markdown_to_html(markdown_content: str, theme_name: str) -> str:
    """Convert markdown to HTML with embedded CSS styling"""
    
    # Preprocess markdown to fix nested list formatting
    processed_markdown = preprocess_markdown_for_nested_lists(markdown_content)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        processed_markdown,
        extensions=['extra', 'codehilite', 'toc'],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': False
            }
        }
    )
    
    # Load theme CSS
    css_content = load_theme_css(theme_name)
    
    # Create complete HTML document with embedded CSS
    complete_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Converted Document</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <div class="container">
{html_content}
    </div>
</body>
</html>"""
    
    return complete_html

@app.get("/")
async def root():
    """API root endpoint with basic information"""
    return {
        "message": "Markdown to HTML Converter API",
        "version": "1.0.0",
        "available_themes": AVAILABLE_THEMES,
        "endpoints": {
            "convert": "/convert",
            "themes": "/themes",
            "health": "/health"
        }
    }

@app.get("/themes")
async def get_available_themes():
    """Get list of available CSS themes"""
    return {
        "available_themes": AVAILABLE_THEMES,
        "default_theme": "mocha-minimalist"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "md-to-html-converter"}

@app.post("/convert", response_model=ConversionResponse)
async def convert_markdown(request: MarkdownRequest):
    """Convert Markdown content to HTML with specified theme"""
    
    try:
        # Validate theme
        if request.theme not in AVAILABLE_THEMES:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid theme. Available themes: {', '.join(AVAILABLE_THEMES)}"
            )
        
        # Validate markdown content
        if not request.markdown_content.strip():
            raise HTTPException(
                status_code=400,
                detail="Markdown content cannot be empty"
            )
        
        # Convert markdown to HTML
        html_result = convert_markdown_to_html(request.markdown_content, request.theme)
        
        return ConversionResponse(
            html_content=html_result,
            theme_used=request.theme,
            success=True,
            message="Conversion successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during conversion: {str(e)}"
        )

@app.get("/convert/preview/{theme}")
async def preview_theme(theme: str, response_class=HTMLResponse):
    """Preview a theme with sample content"""
    
    if theme not in AVAILABLE_THEMES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid theme. Available themes: {', '.join(AVAILABLE_THEMES)}"
        )
    
    sample_markdown = """# Sample Document

This is a **sample document** to preview the theme styling.

## Features

- Beautiful typography
- Responsive design  
- Modern styling
- Code highlighting

### Code Example

```python
def hello_world():
    print("Hello, World!")
```

### Blockquote

> This is a blockquote example to show how quotes are styled in this theme.

### Table

| Feature | Description |
|---------|-------------|
| Fast | Lightning quick conversion |
| Modern | Contemporary design trends |
| Responsive | Works on all devices |

---

*This is italic text* and this is `inline code`.
"""
    
    html_result = convert_markdown_to_html(sample_markdown, theme)
    return HTMLResponse(content=html_result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

