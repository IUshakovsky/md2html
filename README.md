# Markdown to HTML Converter API

A modern FastAPI-based service that converts Markdown content to beautifully styled HTML with multiple contemporary CSS themes. 

## Features

- **7 Modern CSS Themes**: Choose from carefully crafted themes based on 2025 design trends
- **No External Dependencies**: All themes use system fonts and pure CSS
- **Responsive Design**: All themes work perfectly on desktop and mobile devices
- **Fast Conversion**: Lightning-quick Markdown to HTML processing
- **RESTful API**: Clean, well-documented API endpoints
- **Theme Preview**: Preview any theme with sample content

## Available Themes

### 1. Mocha Minimalist
*Inspired by Pantone 2025 Color of the Year - Mocha Mousse*
- Warm brown color palette with cream and soft whites
- Elegant serif typography for headings
- Clean, minimal design with generous whitespace
- Perfect for: Blogs, documentation, personal websites

### 2. Neon Brutalist
*Anti-design trend with bold contrasts*
- Black background with electric green, blue, and pink accents
- Bold, aggressive typography
- Raw, unpolished aesthetic with intentional imperfections
- Perfect for: Creative portfolios, tech blogs, experimental content

### 3. Glassmorphism Pro
*Modern glass-like transparency effects*
- Translucent glass elements with backdrop blur
- Gradient backgrounds with floating elements
- Soft shadows and modern spacing
- Perfect for: Modern apps, design showcases, tech companies

### 4. Sunset Gradient
*Vibrant warm gradients trending in 2025*
- Orange, pink, and purple gradient combinations
- Energetic and visually striking design
- Smooth color transitions and modern typography
- Perfect for: Creative agencies, marketing content, lifestyle brands

### 5. Dark Sage
*Sustainable design with nature-inspired colors*
- Deep greens, sage, cream, and charcoal palette
- Eco-friendly aesthetic with natural elements
- Calming and sophisticated design
- Perfect for: Environmental content, wellness brands, organic products

### 6. Corporate Blue
*Professional and trustworthy for business content*
- Navy blue, light blue, and white color scheme
- Clean, professional typography and layout
- Business-appropriate styling with clear hierarchy
- Perfect for: Corporate websites, business documentation, professional blogs

### 7. Retro Tech
*Nostalgic computing aesthetics with modern twist*
- Terminal green, amber, and black color scheme
- Monospace fonts with retro computing feel
- Glowing effects and terminal-inspired design
- Perfect for: Tech blogs, developer documentation, gaming content

## API Endpoints

### GET `/`
Returns API information and available themes.

**Response:**
```json
{
  "message": "Markdown to HTML Converter API",
  "version": "1.0.0",
  "available_themes": ["mocha-minimalist", "neon-brutalist", "glassmorphism-pro", "sunset-gradient", "dark-sage", "corporate-blue", "retro-tech"],
  "endpoints": {
    "convert": "/convert",
    "themes": "/themes",
    "health": "/health"
  }
}
```

### GET `/themes`
Returns list of available themes.

**Response:**
```json
{
  "available_themes": ["mocha-minimalist", "neon-brutalist", "glassmorphism-pro", "sunset-gradient", "dark-sage", "corporate-blue", "retro-tech"],
  "default_theme": "mocha-minimalist"
}
```

### POST `/convert`
Converts Markdown content to styled HTML.

**Request Body:**
```json
{
  "markdown_content": "# Your Markdown Content\n\nThis is **bold** text.",
  "theme": "mocha-minimalist"
}
```

**Response:**
```json
{
  "html_content": "<!DOCTYPE html><html>...</html>",
  "theme_used": "mocha-minimalist",
  "success": true,
  "message": "Conversion successful"
}
```

### GET `/convert/preview/{theme}`
Preview a theme with sample content.

**Parameters:**
- `theme`: Theme name (e.g., "mocha-minimalist")

**Response:** HTML page with sample content styled with the specified theme.

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "md-to-html-converter"
}
```

## Installation & Setup

### Prerequisites
- Python 3.11+
- pip

### Local Development

1. **Clone or download the project:**
```bash
git clone <repository-url>
cd md-to-html-api
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the server:**
```bash
python app/main.py
```

The API will be available at `http://localhost:8000`

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "app/main.py"]
```

## Usage Examples

### Python Example
```python
import requests

# Convert markdown to HTML
response = requests.post("http://localhost:8000/convert", json={
    "markdown_content": "# Hello World\n\nThis is **bold** text.",
    "theme": "glassmorphism-pro"
})

result = response.json()
html_output = result["html_content"]
```

### cURL Example
```bash
curl -X POST "http://localhost:8000/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_content": "# Hello World\n\nThis is **bold** text.",
    "theme": "neon-brutalist"
  }'
```

### JavaScript Example
```javascript
const response = await fetch('http://localhost:8000/convert', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    markdown_content: '# Hello World\n\nThis is **bold** text.',
    theme: 'sunset-gradient'
  })
});

const result = await response.json();
const htmlOutput = result.html_content;
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Invalid theme or empty markdown content
- `500 Internal Server Error`: Server-side processing errors

Example error response:
```json
{
  "detail": "Invalid theme. Available themes: mocha-minimalist, neon-brutalist, glassmorphism-pro, sunset-gradient, dark-sage, corporate-blue, retro-tech"
}
```

## Performance

- **Fast Processing**: Optimized Markdown parsing and HTML generation
- **Lightweight**: No external font dependencies or heavy libraries
- **Scalable**: Stateless design suitable for horizontal scaling
- **Efficient**: Minimal memory footprint and CPU usage

## Browser Support

All themes are tested and compatible with:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+


## Support

For questions, issues, or feature requests, please contact the development team.

---

**Built with modern web technologies and 2025 design trends in mind.**

