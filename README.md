# ROV Manual Chatbot

Cloud-hosted technical manual chatbot for Subsea 7 ROV operations.
Built by Sean Brock — Electronic Systems Specialist.

## Stack
- **Frontend**: Single-page HTML/JS app
- **Backend**: Flask proxy server (Python)
- **Embeddings**: Voyage AI (`voyage-large-2`)
- **Vector DB**: Supabase (pgvector)
- **LLM**: Anthropic Claude Sonnet

## How it works
1. Upload a PDF technical manual
2. Text is extracted, chunked into ~400-word sections
3. Each chunk is converted to a meaning-vector by Voyage AI
4. Vectors stored permanently in Supabase
5. Questions are matched by meaning (not keywords) against stored vectors
6. Relevant chunks sent to Claude for accurate answers with page citations

## Deployment
Deployed on Railway. Set no environment variables — all API keys are entered
by the user in the browser UI and never stored server-side.

## Local development
```bash
pip install -r requirements.txt
python app.py
```
Then open http://localhost:8000
# v2 - drawing tool enabled
