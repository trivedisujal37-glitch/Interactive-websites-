# Supply Chain Optimization System — Anshu's Implementation

Final-year BCA group project: Supply Chain Optimization System.
This component represents **Anshu's portion**: Cost Analysis, Optimization, Recommendations, Reporting, Export & App Integration.

---

## 1. What's Implemented

- **`modules/cost.py`**:
  - `analyze_cost(df, item_col=None, category_col=None) -> CostAnalysisResult`
  - Honest handling of missing/partial cost columns (`SUPPORTED_COST_COLUMNS = ["Unit Price", "Purchase Cost", "Holding Cost", "Transportation Cost"]`).
  - Item-level and category-level cost aggregation with descending sort by total cost.
  - Zero currency assumptions or invented figures. Returns `UNAVAILABLE_MESSAGE` if no supported cost columns exist.
- **`modules/optimization.py`**:
  - Pure calculation engine `find_optimization_issues()` converting inventory and evidence into observational findings.
  - Generates `Reorder Review`, `Overstock Review`, `Demand Coverage Risk`, and `Predicted Demand Coverage Risk`.
  - Never issues automated commands or orders; produces strictly observational data with real calculated differences.
  - Integration wrapper `run_optimization()` with non-breaking placeholder hooks for teammates' modules.
- **`modules/recommendations.py`**:
  - `build_recommendations(findings) -> RecommendationResult`
  - Strict human review enforcement: every recommendation mandates `HUMAN_REVIEW_TEXT = "Human approval required. This is not an automated action."`.
  - Zero command verbs (e.g., forbidden "Order more inventory" is never used). Always phrases suggested actions as `"Recommended for review: ..."`.
  - Schema adherence across 9 required fields per recommendation.
- **`utils/export.py`**:
  - `export_to_csv(df)`: Exports UTF-8 encoded CSV bytes.
  - `export_to_excel(df)`: Exports `.xlsx` bytes if `openpyxl` is installed.
  - `get_available_export_formats()`: Dynamically advertises supported formats.
- **`app.py`**:
  - Streamlit multi-page interface with exact 10 navigation pages in specified order.
  - 4-card KPI dashboard with fallback `"Unavailable"` indicators (no fake placeholders).
  - Explicit `"not yet available"` notices for pages owned by Sujal and Manthan.
  - Shared CSV and Excel download buttons for all tabular outputs.
- **`tests/`**:
  - Complete pytest test suite covering unit and end-to-end integration workflows.
- **`sample_data.csv`**:
  - Realistic synthetic supply chain dataset demonstrating healthy, understock, and overstock scenarios.

---

## 2. Expected Dataset Columns

The application and analysis modules accept standard CSV files with the following supported column headers:

| Category | Supported Column Names | Required / Optional |
|---|---|---|
| **Item Identifier** | `Item`, `Item Name`, `Product`, `Product Name`, `SKU`, `Item ID` (falls back to first column) | Recommended |
| **Category** | `Category`, `category`, `Item Category`, `Product Category` | Optional |
| **Inventory** | `Current Stock`, `Reorder Point`, `Max Stock Level` | Required for Optimization |
| **Cost Columns** | `Unit Price`, `Purchase Cost`, `Holding Cost`, `Transportation Cost` | Any combination (1 to 4) |

---

## 3. Teammate Integration Contract (Sujal & Manthan)

To wire teammates' upcoming work into `modules/optimization.py`'s `run_optimization()` wrapper, the following interfaces and contracts are established:

### A. Demand Module (Sujal / Manthan)
- **Module Path:** `modules.demand`
- **Function Name:** `get_demand_dataframe() -> pd.DataFrame`
- **Expected Return:**
  - A pandas DataFrame containing:
    - Item identifier matching the inventory item column (e.g., `Item`)
    - `Demand`: Numeric column representing recorded or recent demand.
- **Behavior when unavailable:** Handled gracefully via `_try_import_demand_df()` returning `None`.

### B. Prediction Module (Sujal / Manthan)
- **Module Path:** `modules.prediction`
- **Function Name:** `get_prediction_dataframe() -> pd.DataFrame`
- **Expected Return:**
  - A pandas DataFrame containing:
    - Item identifier matching the inventory item column (e.g., `Item`)
    - `Predicted Demand`: Numeric column representing forecasted demand.
- **Behavior when unavailable:** Handled gracefully via `_try_import_prediction_df()` returning `None`.

### C. Supplier Module (Sujal / Manthan)
- **Module Path:** `modules.supplier`
- **Function Name:** `get_supplier_dataframe() -> pd.DataFrame`
- **Expected Return:**
  - A pandas DataFrame containing item identifier and supplier lead times or risk factors.
- **Behavior when unavailable:** Handled gracefully via `_try_import_supplier_df()` returning `None`.

---

## 4. Out of Scope

The following items are strictly out of scope for this deliverable:
- Databases (MongoDB, MySQL, PostgreSQL, SQLite)
- Full-stack web frameworks (Django, Flask, FastAPI, React)
- Automatic procurement / auto-ordering
- Automatic supplier contact
- Supplier ranking / arbitrary scoring algorithms
- Fake AI or LLM wrapper hallucinations
- External production APIs
- Unnecessary UI animations or unrequested abstractions

---

## 5. Running the Application & Tests

### Installation
```bash
pip install -r requirements.txt
```

### Running Tests
```bash
python -m pytest tests/ -v
```

### Launching Streamlit App
```bash
streamlit run app.py
```
