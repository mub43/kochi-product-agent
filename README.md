# Kochi Product-Idea Agent

I built this FastAPI application to transform product concepts into actionable insights using Google's Gemini AI. It generates structured product ideas with consumer hooks, competitor analysis, and prototype tasks—everything you need to quickly evaluate a product opportunity.

## What It Does

I designed this to return three key components for every product concept:
- **Consumer Hook**: A compelling value proposition that would attract consumers
- **Competitor or Trend**: Key market competitors or trends to consider
- **Prototype Task**: A specific, actionable task for prototyping the product

The entire application runs as a single-file FastAPI app with a clean web interface, making it easy to deploy and use.

## Tech Stack

I'm using:
- **FastAPI** for the web framework and API endpoints
- **Pydantic** for data validation and type safety
- **Google Gemini 2.0 Flash** for AI-powered product ideation
- **Uvicorn** as the ASGI server
- **Python 3.11+** (required)

## Getting Started

You'll need Python 3.11+ and a Google Gemini API key ([get one here](https://makersuite.google.com/app/apikey)).

1. Clone the repo:
   ```bash
   git clone https://github.com/mub43/kotchi.ai.git
   cd kotchi.ai
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API key by creating a `.env` file:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

4. Start the server:
   ```bash
   python main.py
   ```
   
   Or run with uvicorn directly:
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000
   ```

5. Open http://localhost:8000 in your browser

## How to Use It

### Web Interface

Just type a product concept and hit "Generate Product Idea". I've tested it with concepts like:
- "AI-powered fitness tracker"
- "Sustainable packaging solution"
- "Voice-controlled home automation"

### API Endpoint

I also exposed a REST API endpoint you can call directly:

```bash
curl -X POST "http://localhost:8000/generate-idea" \
  -H "Content-Type: application/json" \
  -d '{"concept": "AI-powered fitness tracker"}'
```

Here's what you'll get back:
```json
{
  "consumer_hook": "Transform your daily routine into personalized fitness insights with AI that learns your body's unique patterns",
  "competitor_or_trend": "Competing with Fitbit and Apple Watch, but leveraging the growing trend of AI personalization in health tech",
  "prototype_task": "Build a minimal MVP that tracks basic activity metrics and uses a simple ML model to provide one personalized insight per day"
}
```

## Project Structure

I kept it simple with a single-file architecture:

```
kotchi.ai/
├── main.py              # Everything in one file
├── .env                 # Your API key (gitignored)
├── .cursor.json         # Code standards config
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## How I Built It

When you submit a concept, here's the flow:

1. The FastAPI endpoint receives your product concept
2. I send it to Gemini with a prompt that tells the model to act as a "concise consumer product strategist"
3. The AI's JSON response gets parsed and validated using Pydantic's `ProductIdea` schema
4. Results are returned to the frontend and displayed

I spent time on the prompt engineering to ensure the AI returns exactly the three components in valid JSON format—no markdown, no extra text, just clean structured data.

## Code Standards

I set up `.cursor.json` to enforce:
- PEP8 style guide
- Google-style docstrings
- Type hints everywhere
- F-strings for formatting
- 100 character max line length

## Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)

## License

MIT License - use it however you want!

## Contributing

I'm open to contributions! Submit issues, fork the repo, or send pull requests. Let's make this better together.


