# 🧠 Code Insight Pro

A **Streamlit-based AI-powered codebase explorer** that lets you load any Python repository (via Git URL or ZIP upload), visualize its file and function relationships as an interactive graph, and chat with an AI assistant to understand, explain, and explore your code.

---

## ✨ Features

- 📂 **Load repositories** from a Git URL or a local ZIP file
- 🕸️ **Interactive dependency graph** — visualizes file imports and function call relationships using `vis.js`
- 🔍 **File explorer** with search and tree navigation
- 💬 **AI-powered code explanation** — ask questions about any file or function using OpenRouter-hosted LLMs
- 🎨 **Dark-themed UI** built with Streamlit and custom CSS
- ⚡ **Semantic embeddings** for context-aware AI responses (`all-MiniLM-L6-v2`)

---

## 🗂️ Project Structure

```
code-analyzer-and-view-main/
│
├── main_app.py           # Main Streamlit app entry point
├── run.py                # Startup script (checks deps, launches app)
├── test.py               # Basic tests
├── .env                  # Environment variables (API keys, model settings)
│
├── config/
│   └── settings.py       # App configuration and theme settings
│
├── core/
│   ├── analyzer.py       # Python AST-based code analyzer
│   ├── explainer.py      # OpenRouter AI explainer (OpenAI-compatible)
│   ├── file_manager.py   # File loading and management
│   └── graph_builder.py  # Builds dependency graph using NetworkX
│
├── ui/
│   ├── file_explorer.py  # Sidebar file tree UI component
│   └── graph_renderer.py # Renders interactive vis.js graph
│
├── utils/
│   ├── git_utils.py      # Git repository cloning
│   └── zip_utils.py      # ZIP extraction helpers
│
└── lib/                  # Vendored JS/CSS libraries
    ├── vis-9.1.2/        # vis-network for graph rendering
    ├── tom-select/       # Dropdown select library
    └── bindings/         # JS utility bindings
```

---

## ⚙️ Prerequisites

- Python **3.9+** (developed and tested on Python 3.11)
- An **OpenRouter API key** — get one free at [openrouter.ai/keys](https://openrouter.ai/keys)
- `git` installed and available on your system PATH (required for cloning repos)

---

## 🚀 Getting Started

### 1. Clone this repository

```bash
git clone https://github.com/karthik26-Thalari/code-analyzer-and-view.git
cd code-analyzer-and-view
```

### 2. Create a virtual environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> If you don't have a `requirements.txt` yet, install the core packages manually:
> ```bash
> pip install streamlit networkx pyvis openai gitpython python-magic sentence-transformers python-dotenv
> ```

### 4. Configure your environment

Copy the example env file and fill in your API key:

```bash
cp .env.example .env
```

Then open `.env` and update the values:

```env
# Required
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Choose any model from openrouter.ai/models (free ones work great)
OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct:free

# Optional tuning
EMBEDDING_MODEL=all-MiniLM-L6-v2
TEMPERATURE=0.3
MAX_TOKENS=5000
```

### 5. Run the app

**Option A — using the launcher script (recommended):**
```bash
python run.py
```

**Option B — run Streamlit directly:**
```bash
streamlit run main_app.py
```

Then open your browser at **[http://localhost:8501](http://localhost:8501)**

---

## 🖥️ How to Use

1. **Load a repository** — paste a GitHub URL or upload a `.zip` file of your project in the sidebar
2. **Explore the graph** — the main panel renders an interactive dependency graph; click any node to inspect that file or function
3. **Browse files** — use the file tree in the sidebar to navigate and view source code
4. **Ask the AI** — type a question in the AI chat panel (e.g. *"What does `analyzer.py` do?"* or *"Explain the graph builder logic"*) and get an explanation powered by your chosen LLM

---

## 🔑 Supported AI Models (via OpenRouter)

Any model available on [openrouter.ai](https://openrouter.ai/models) works. Some popular free options:

| Model | ID |
|---|---|
| Llama 3.1 70B | `meta-llama/llama-3.1-70b-instruct:free` |
| Mistral 7B | `mistralai/mistral-7b-instruct:free` |
| Gemma 2 9B | `google/gemma-2-9b-it:free` |
| MiMo V2 Flash | `xiaomi/mimo-v2-flash:free` |

Set your chosen model in the `.env` file under `OPENROUTER_MODEL`.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `Import error` on startup | Run `pip install -r requirements.txt` inside your virtual environment |
| `OPENROUTER_API_KEY is required` | Make sure your `.env` file exists and has a valid key |
| Graph not displaying | Confirm the `lib/` folder is present alongside `main_app.py` |
| Git clone fails | Ensure `git` is installed: `git --version` |
| `python-magic` error on Windows | Install `python-magic-bin`: `pip install python-magic-bin` |

---

## 📄 License

This project is open source. Feel free to fork, modify, and build on it.

---

## 🙌 Acknowledgements

- [Streamlit](https://streamlit.io/) — UI framework
- [vis.js](https://visjs.org/) — graph visualization
- [OpenRouter](https://openrouter.ai/) — LLM API gateway
- [NetworkX](https://networkx.org/) — graph data structures
- [Sentence Transformers](https://www.sbert.net/) — semantic embeddings
