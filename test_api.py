#!/usr/bin/env python3
"""
Test script for Markdown to HTML Converter API
Demonstrates all API endpoints and functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    print("🚀 Testing Markdown to HTML Converter API")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working")
            print(f"   Available themes: {len(data['available_themes'])}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 2: Health check
    print("\n2. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 3: Themes endpoint
    print("\n3. Testing themes endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/themes")
        if response.status_code == 200:
            data = response.json()
            print("✅ Themes endpoint working")
            print(f"   Default theme: {data['default_theme']}")
        else:
            print(f"❌ Themes endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Themes endpoint error: {e}")
    
    # Test 4: Conversion with different themes
    print("\n4. Testing conversion endpoint...")
    
    sample_markdown = """# Test Document

This is a **test document** to verify the API functionality.

## Features

- Markdown to HTML conversion
- Multiple beautiful themes
- Responsive design
- No external dependencies

### Code Example

```python
def hello_world():
    print("Hello from the API!")
```

> This is a blockquote to test styling.

| Feature | Status |
|---------|--------|
| Conversion | ✅ Working |
| Themes | ✅ Working |
| API | ✅ Working |
"""

    themes_to_test = ["mocha-minimalist", "neon-brutalist", "glassmorphism-pro"]
    
    for theme in themes_to_test:
        print(f"\n   Testing theme: {theme}")
        try:
            response = requests.post(f"{BASE_URL}/convert", json={
                "markdown_content": sample_markdown,
                "theme": theme
            })
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    html_length = len(data["html_content"])
                    print(f"   ✅ {theme}: Converted successfully ({html_length} chars)")
                else:
                    print(f"   ❌ {theme}: Conversion failed - {data['message']}")
            else:
                print(f"   ❌ {theme}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {theme}: Error - {e}")
    
    # Test 5: Error handling
    print("\n5. Testing error handling...")
    
    # Test invalid theme
    try:
        response = requests.post(f"{BASE_URL}/convert", json={
            "markdown_content": "# Test",
            "theme": "invalid-theme"
        })
        if response.status_code == 400:
            print("✅ Invalid theme error handling works")
        else:
            print(f"❌ Invalid theme should return 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid theme test error: {e}")
    
    # Test empty content
    try:
        response = requests.post(f"{BASE_URL}/convert", json={
            "markdown_content": "",
            "theme": "mocha-minimalist"
        })
        if response.status_code == 400:
            print("✅ Empty content error handling works")
        else:
            print(f"❌ Empty content should return 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Empty content test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")
    print("\n💡 To preview themes in browser, visit:")
    for theme in ["mocha-minimalist", "neon-brutalist", "glassmorphism-pro", "sunset-gradient", "dark-sage", "corporate-blue", "retro-tech"]:
        print(f"   {BASE_URL}/convert/preview/{theme}")

if __name__ == "__main__":
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    test_api()

