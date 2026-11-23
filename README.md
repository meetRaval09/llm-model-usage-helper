# LLM Model Usage Helper

Save your AI chats locally so they are never locked inside one provider.

**v0.1.0 - Capture and store.** A Chrome extension reads the open ChatGPT/Claude chat and sends it to a local FastAPI backend, which stores it in SQLite.

## Run
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
Load the `extension` folder in Chrome (chrome://extensions, Developer mode, Load unpacked), open a chat, click the extension, and press save.

Your chats stay in `backend/memory.db` on your computer and are never committed.
