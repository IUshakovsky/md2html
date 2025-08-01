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

def preprocess_markdown_for_nested_lists(markdown_content: str) -> str:
    """Fix common nested list formatting issues for proper Markdown parsing"""
    # The old implementation was overly complex, let's use a simpler approach
    # that specifically addresses the known issues
    
    # Main issues to fix:
    # 1. Convert 2-space indented list items to 4-space for proper nesting
    # 2. Ensure ordered lists are processed correctly
    # 3. Remove excessive blank lines
    # 4. Preserve citations section formatting
    
    lines = markdown_content.split('\n')
    result = []
    in_citations = False
    
    # First pass: Fix indentation for nested lists
    for i, line in enumerate(lines):
        # Handle citations section
        if line.strip().lower().startswith('citations:'):
            in_citations = True
            result.append(line)
            # Ensure proper line break after citations header
            if i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].strip().startswith('['):
                result.append('')
            continue
            
        # Don't process citations section
        if in_citations:
            result.append(line)
            continue
        
        # Convert 2-space indentation to 4-space for proper nesting
        # Handle both unordered lists (- *) and ordered lists (1. 2. etc.)
        stripped = line.lstrip()
        is_unordered = stripped.startswith('- ') or stripped.startswith('* ')
        is_ordered = False
        
        # Check if it's an ordered list item (starts with number followed by dot and space)
        if not is_unordered and len(stripped) > 2:
            parts = stripped.split('. ', 1)
            if len(parts) == 2 and parts[0].isdigit():
                is_ordered = True
        
        if is_unordered or is_ordered:
            indent = len(line) - len(line.lstrip())
            if 0 < indent < 4:  # If indented but not enough
                result.append('    ' + line.lstrip())
            else:
                result.append(line)
        else:
            result.append(line)
    
    # Second pass: Remove excessive blank lines and ensure proper spacing
    final_result = []
    prev_blank = False
    prev_is_list_item = False
    list_block_started = False
    
    for i, line in enumerate(result):
        is_blank = not line.strip()
        is_list_item = (line.lstrip().startswith('- ') or 
                        line.lstrip().startswith('* ') or
                        (line.strip() and line.strip()[0].isdigit() and '. ' in line.strip()))
        is_indented = len(line) > len(line.lstrip()) and len(line.lstrip()) > 0
        
        # Skip multiple blank lines
        if is_blank and prev_blank:
            continue
            
        # Add blank line before a list item that follows non-list content
        if is_list_item and not is_indented and not prev_is_list_item and not prev_blank and i > 0:
            final_result.append('')
            list_block_started = True
            
        # Don't add blank lines between a list item and its nested items
        if is_blank and prev_is_list_item and i + 1 < len(result) and len(result[i+1]) > len(result[i+1].lstrip()):
            continue
            
        # Add this line
        final_result.append(line)
        prev_blank = is_blank
        
        if not is_blank:
            prev_is_list_item = is_list_item
    
    # Ensure proper ending
    md_text = '\n'.join(final_result)
    if not md_text.endswith('\n'):
        md_text += '\n'
        
    return md_text

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

