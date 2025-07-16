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
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        markdown_content,
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
    uvicorn.run(app, host="0.0.0.0", port=8000)

