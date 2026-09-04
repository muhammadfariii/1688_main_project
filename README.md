# 1688 Sourcing Tool (Web Edition)

An Alibaba/1688 supplier sourcing and qualification web application designed to identify likely **source factories and manufacturers**, filter out trading companies and resellers, and evaluate multi-product supplier catalog coverage.

---

## 🌟 Key Features

1. **Single Product Factory Search**:
   - Query 1688 suppliers for a single product category.
   - Automatically classifies each seller as **Factory**, **Trading Company**, or **Uncertain** using a multi-signal heuristic engine.
   - Ranks results with verified source factories and highest confidence first.
   - Inspect granular heuristic signals (plant area, workforce, registered capital, audit badges, Chinese business scope keywords).

2. **Multiple Products Coverage Search**:
   - Paste 5–15 products (one per line) in a category (e.g. kitchenware, stationery, fitness equipment).
   - Aggregates supplier offerings to determine **how many requested items each supplier can produce/supply**.
   - Calculates **Products Covered**, **Coverage %**, and composite capability score.
   - Highlights covered products vs missing items.

3. **One-Click Export**:
   - Export single search and multi-search results to formatted **Excel (.xlsx)** workbooks with styling and hyperlinks.
   - Export to **CSV** encoded with UTF-8 BOM (`utf-8-sig`) for Excel compatibility across Windows and macOS.

4. **Zero-Configuration Demo Mode**:
   - Works immediately out of the box without any API keys using realistic mock supplier data from Chinese industrial hubs (Yongkang, Yiwu, Dongguan, Chaozhou, Shenzhen, Ningbo, etc.).

5. **Pluggable Provider Architecture**:
   - Abstract adapter layer (`BaseProviderAdapter`) allows swapping between `DemoAdapter` and live providers (e.g., `Apify1688Adapter`) without modifying frontend or business logic.
   - Sensitive credentials remain strictly server-side.

---

## 🏗️ Architecture

```text
       Browser (Public Web UI)
                 │
                 ▼
       FastAPI Web Server (app.py)
                 │
        ┌────────┴────────┐
        ▼                 ▼
   Search Engine      Exporter
 (search_engine.py)  (exporter.py)
        │
   Classifier (classifier.py)
        │
  Provider Adapter (adapters.py)
   ┌────┴────────────────────────┐
   ▼                             ▼
DemoAdapter (Mock)       Apify1688Adapter (Live API)
```

---

## 🚀 How to Deploy to GitHub

### Option A: Push the Existing Repository to GitHub
1. Create a new repository on [GitHub](https://github.com/new) (e.g., `1688-sourcing-tool`). Leave it empty (do not initialize with README or .gitignore).
2. In your terminal, navigate to the project directory and run:
   ```bash
   cd 1688_sourcing_tool
   git remote add origin https://github.com/<your-username>/1688-sourcing-tool.git
   git branch -M main
   git push -u origin main
   ```

### Option B: Clone or Upload Directly
You can also use GitHub Desktop, upload files through the GitHub web UI, or use GitHub CLI:
```bash
gh repo create 1688-sourcing-tool --public --source=. --remote=origin --push
```

---

## ☁️ How to Deploy on Replit (Public Web Link)

### Method 1: Import directly from GitHub into Replit (Recommended)
1. Go to [Replit.com](https://replit.com) and click **Create Repl**.
2. Select **Import from GitHub** in the top right.
3. Enter your repository URL (e.g., `https://github.com/<your-username>/1688-sourcing-tool`).
4. Replit will automatically detect the `.replit` configuration and install dependencies from `requirements.txt`.
5. Click **Run** (or Replit Deployments). Your web app will open immediately with a public URL:
   ```text
   https://<your-repl-name>.<your-username>.replit.app
   ```

### Method 2: Manual Upload on Replit
1. Create a new Python Repl on Replit.
2. Upload the project files / extract `1688_sourcing_tool.zip`.
3. Ensure `.replit` and `requirements.txt` are in the project root.
4. Click **Run**.

---

## ⚙️ Environment Variables & Secrets Configuration

If running in **Demo Mode**, no configuration or API keys are required.

To connect a live provider API later:
1. In Replit Secrets (Lock icon) or in a `.env` file (server-side only):
   - `PROVIDER_API_KEY`: Your 1688 provider API token.
   - `PROVIDER_NAME`: `apify` (or custom provider).
   - `PROVIDER_BASE_URL`: (Optional) Provider endpoint URL.
   - `DEMO_MODE`: Set to `false` when enabling live API mode.

---

## 💻 Local Run Instructions

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/1688-sourcing-tool.git
cd 1688-sourcing-tool

# 2. (Optional) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the web application
python app.py
# or: uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser at `http://localhost:8000`.

---

## 🧪 Running Automated Tests

The test suite covers classifier accuracy, adapter fallback, search engine aggregation, Excel/CSV generation, and all FastAPI REST endpoints.

```bash
python -m unittest discover -s tests
```

---

## 📁 Project Structure

| File / Folder | Purpose |
|---|---|
| `app.py` | FastAPI application, web routes, REST API endpoints, static file mounting |
| `classifier.py` | Heuristic multi-signal factory vs. trading company classification engine |
| `adapters.py` | Provider adapter interface (`BaseProviderAdapter`), `DemoAdapter`, `Apify1688Adapter` |
| `search_engine.py` | Single-product ranking & multi-product coverage aggregation engine |
| `exporter.py` | Formatted Excel (`.xlsx`) and CSV (`utf-8-sig`) export generators |
| `config.py` | Configuration manager (reads environment variables, Replit secrets, local fallback) |
| `static/index.html` | Responsive single-page web frontend (HTML/CSS/JS) |
| `requirements.txt` | Python dependencies (FastAPI, Uvicorn, Openpyxl, Requests, etc.) |
| `.replit` & `replit.nix` | Replit runner and deployment specifications |
| `.github/workflows/ci.yml` | GitHub Actions CI workflow to run automated tests on push |
| `.gitignore` | Standard Git ignore configuration for Python, caches, and secrets |
| `tests/test_sourcing_tool.py` | Complete unittest suite for all modules |

---

## ⚠️ Important Real-World Note on 1688 API Data
- Third-party 1688 providers do not maintain a universal standardized schema.
- Factory classification is heuristic/signal-based because 1688 vendor registrations can vary.
- The `Apify1688Adapter` skeleton is ready to be mapped to your chosen vendor's live API response format when API documentation is provided.
