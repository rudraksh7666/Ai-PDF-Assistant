# 📄 AI PDF Assistant

Upload a PDF and chat with it. Ask questions, get a summary, or translate the whole document, powered by the Google Gemini API and built with Streamlit.

## Features

- **Ask a question**: answers come only from the uploaded document, and the model says so when the answer isn't there
- **Summarize**: short (5 bullets) or detailed, section by section
- **Translate**: into Hindi, Punjabi, Spanish, French, German, Japanese, Arabic, Portuguese or English
- **Download** any result as a Markdown file
- Clear messages for scanned PDFs, invalid keys, rate limits and unavailable models

## Tech stack

Python · Streamlit · Google Gen AI SDK (`google-genai`) · pypdf · prompt engineering

## Run it locally

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Gemini API key (free at https://aistudio.google.com/apikey)
copy .streamlit\secrets.toml.example .streamlit\secrets.toml     # Windows
# cp .streamlit/secrets.toml.example .streamlit/secrets.toml     # macOS / Linux
# then open secrets.toml and paste your key

# 4. Start the app
streamlit run app.py
```

No `secrets.toml`? You can also paste your key into the sidebar while the app is running.

## Notes

- Your API key is read from `.streamlit/secrets.toml` or the `GEMINI_API_KEY` environment variable and is never hard-coded. `secrets.toml` is listed in `.gitignore`.
- The default model is set at the top of `app.py` (`DEFAULT_MODEL`) and can be changed from the sidebar or with `GEMINI_MODEL`. Gemini retires older models regularly, so update it if you see a "model not available" message.
- Only the first 60,000 characters of very long PDFs are used.
- Scanned (image-only) PDFs aren't supported because there is no OCR step.

## Possible improvements

- OCR for scanned PDFs
- Chunking plus embeddings for book-length documents
- Multi-PDF question answering
- Chat history with follow-up questions

## What I learned

Working with the Gemini API, extracting text from PDFs, prompt design that keeps answers grounded in a document, and managing API keys safely.
