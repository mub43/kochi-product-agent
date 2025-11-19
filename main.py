"""
Kochi Product-Idea Agent - FastAPI Application.

A single-file FastAPI application that generates product ideas using
Google's Gemini API.
"""

import os
import json
from typing import Dict, Any
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

# Load environment variables from .env file (override existing)
load_dotenv(override=True)

# Initialize FastAPI app
app = FastAPI(title="Kochi Product-Idea Agent", version="1.0.0")

# Gemini API configuration
GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)


class ProductIdea(BaseModel):
    """Pydantic model for product idea response."""

    consumer_hook: str = Field(..., description="Consumer hook for the product")
    competitor_or_trend: str = Field(
        ..., description="Competitor or trend analysis"
    )
    prototype_task: str = Field(..., description="Prototype task description")


class ConceptRequest(BaseModel):
    """Request model for product concept."""

    concept: str = Field(..., description="Product concept to analyze")


async def generate_product_idea(concept: str) -> ProductIdea:
    """
    Generate product idea components using Gemini API.

    Args:
        concept: The product concept to analyze.

    Returns:
        ProductIdea: Structured product idea with three components.

    Raises:
        HTTPException: If API call fails or response is invalid.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY environment variable not set",
        )
    # Strip any whitespace from the API key
    api_key = api_key.strip()

    prompt = f"""You are a concise consumer product strategist. 
    Based on the following product concept: "{concept}"
    
    Generate a product idea with exactly three components:
    1. consumer_hook: A compelling hook that would attract consumers
    2. competitor_or_trend: Key competitor or market trend to consider
    3. prototype_task: A specific task for prototyping this product
    
    Return ONLY valid JSON in this exact format:
    {{
        "consumer_hook": "...",
        "competitor_or_trend": "...",
        "prototype_task": "..."
    }}
    
    Do not include any markdown formatting, code blocks, or additional text.
    Only return the JSON object."""

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": api_key
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GEMINI_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            # Extract text from Gemini response
            if "candidates" not in data or not data["candidates"]:
                raise HTTPException(
                    status_code=500,
                    detail="No candidates in Gemini API response"
                )

            text_content = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Clean up the response (remove markdown code blocks if present)
            text_content = text_content.strip()
            if text_content.startswith("```json"):
                text_content = text_content[7:]
            if text_content.startswith("```"):
                text_content = text_content[3:]
            if text_content.endswith("```"):
                text_content = text_content[:-3]
            text_content = text_content.strip()

            # Parse JSON response
            idea_data = json.loads(text_content)
            return ProductIdea(**idea_data)

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Gemini API error: {e.response.text}"
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse Gemini response as JSON: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@app.post("/generate-idea", response_model=ProductIdea)
async def generate_idea(request: ConceptRequest) -> ProductIdea:
    """
    Generate product idea based on concept.

    Args:
        request: ConceptRequest containing the product concept.

    Returns:
        ProductIdea: Generated product idea with three components.
    """
    return await generate_product_idea(request.concept)


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    """
    Serve the frontend HTML page.

    Returns:
        str: HTML content for the product idea generator interface.
    """
    return HTML_CONTENT


# Frontend HTML/JS content
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kochi Product-Idea Agent</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
                         Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-align: center;
        }
        
        .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .input-section {
            margin-bottom: 30px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 1.1em;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 14px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 15px;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .results {
            margin-top: 30px;
            display: none;
        }
        
        .results.show {
            display: block;
        }
        
        .result-item {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            animation: fadeIn 0.5s;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .result-label {
            font-weight: 700;
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .result-content {
            color: #333;
            line-height: 1.6;
            font-size: 1em;
        }
        
        .error {
            background: #fee;
            border-left-color: #e74c3c;
            color: #c0392b;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            display: none;
        }
        
        .error.show {
            display: block;
        }
        
        .loading {
            text-align: center;
            color: #667eea;
            font-weight: 600;
            margin-top: 20px;
            display: none;
        }
        
        .loading.show {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Kochi Product-Idea Agent</h1>
        <p class="subtitle">Transform your concept into actionable product insights</p>
        
        <div class="input-section">
            <label for="concept">Product Concept</label>
            <input 
                type="text" 
                id="concept" 
                placeholder="Enter your product concept (e.g., 'AI-powered fitness tracker')"
                autocomplete="off"
            >
            <button id="generateBtn" onclick="generateIdea()">
                Generate Product Idea
            </button>
        </div>
        
        <div class="loading" id="loading">Generating your product idea...</div>
        
        <div class="error" id="error"></div>
        
        <div class="results" id="results">
            <div class="result-item">
                <div class="result-label">Consumer Hook</div>
                <div class="result-content" id="consumerHook"></div>
            </div>
            
            <div class="result-item">
                <div class="result-label">Competitor or Trend</div>
                <div class="result-content" id="competitorTrend"></div>
            </div>
            
            <div class="result-item">
                <div class="result-label">Prototype Task</div>
                <div class="result-content" id="prototypeTask"></div>
            </div>
        </div>
    </div>
    
    <script>
        async function generateIdea() {
            const concept = document.getElementById('concept').value.trim();
            const generateBtn = document.getElementById('generateBtn');
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const results = document.getElementById('results');
            
            // Validation
            if (!concept) {
                error.textContent = 'Please enter a product concept.';
                error.classList.add('show');
                return;
            }
            
            // Reset UI
            error.classList.remove('show');
            results.classList.remove('show');
            loading.classList.add('show');
            generateBtn.disabled = true;
            
            try {
                const response = await fetch('/generate-idea', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ concept: concept })
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Failed to generate idea');
                }
                
                const data = await response.json();
                
                // Display results
                document.getElementById('consumerHook').textContent = 
                    data.consumer_hook;
                document.getElementById('competitorTrend').textContent = 
                    data.competitor_or_trend;
                document.getElementById('prototypeTask').textContent = 
                    data.prototype_task;
                
                results.classList.add('show');
                
            } catch (err) {
                error.textContent = `Error: ${err.message}`;
                error.classList.add('show');
            } finally {
                loading.classList.remove('show');
                generateBtn.disabled = false;
            }
        }
        
        // Allow Enter key to submit
        document.getElementById('concept').addEventListener('keypress', 
            function(e) {
                if (e.key === 'Enter') {
                    generateIdea();
                }
            }
        );
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

