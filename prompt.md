ROLE: Expert Python/Streamlit engineer implementing one member's portion of a
3-person BCA final-year group project called "Supply Chain Optimization System."

TEAM: Sujal, Manthan, Anshu. I am implementing ANSHU's portion only:
Cost Analysis, Optimization, Recommendations, Reporting, Export & App
Integration.

(Apply your ponytail and caveman skills throughout this task.)

============================================================
DELIVERABLES — create exactly these files
============================================================
modules/__init__.py          (empty)
modules/cost.py
modules/optimization.py
modules/recommendations.py
utils/__init__.py            (empty)
utils/export.py
app.py
tests/__init__.py            (empty)
tests/test_cost.py
tests/test_optimization.py
tests/test_recommendations.py
tests/test_export.py
tests/test_end_to_end.py
requirements.txt
sample_data.csv
README_ANSHU.md

============================================================
1. modules/cost.py
============================================================
- Analyze ONLY these columns if present, in any combination: "Unit Price",
  "Purchase Cost", "Holding Cost", "Transportation Cost".
- Never assume currency. Never invent a value for a missing column.
- Define SUPPORTED_COST_COLUMNS list and UNAVAILABLE_MESSAGE =
  "Cost analysis unavailable because no supported cost columns were provided."
- Define a CostAnalysisResult dataclass: available(bool), message(str|None),
  columns_used(list), totals(dict), item_level(DataFrame|None),
  category_level(DataFrame|None).
- Function analyze_cost(df, item_col=None, category_col=None) ->
  CostAnalysisResult:
  - df is None or empty -> return unavailable with UNAVAILABLE_MESSAGE.
  - No supported cost columns present -> return unavailable with
    UNAVAILABLE_MESSAGE.
  - Coerce found cost columns to numeric (errors="coerce").
  - totals = sum of each found column + "Total Combined Cost" = sum of all.
  - If item_col given and exists in df: item_level = per-row cost columns +
    "Total Cost" (row sum), sorted descending by Total Cost.
  - Auto-detect a category column if category_col not given: try
    "Category", "category", "Item Category", "Product Category". If found,
    build category_level = groupby(category).sum() of cost columns +
    "Total Cost", sorted descending.
  - Must work correctly whether 1, 2, 3, or all 4 cost columns are present.

============================================================
2. modules/optimization.py
============================================================
- Purpose: combine evidence from inventory/demand/prediction/supplier/cost
  data into FINDINGS ONLY. NEVER make an automatic decision, NEVER write
  "order X" — only observational findings with real calculated values.
- Define OptimizationResult dataclass: available(bool), message(str|None),
  findings(list[dict]), findings_df(DataFrame|None).
- Core pure function:
  find_optimization_issues(inventory_df=None, demand_df=None,
      prediction_df=None, supplier_df=None, cost_df=None, item_col="Item")
  -> OptimizationResult
  - inventory_df None/empty -> unavailable, message:
    "Optimization unavailable: no inventory data provided."
  - IF "Current Stock" and "Reorder Point" both present:
    for every row where Current Stock < Reorder Point, emit finding:
      finding_type="Reorder Review",
      trigger_condition="Current Stock < Reorder Point",
      current_stock, reorder_point, difference=(stock-reorder),
      explanation="Current Stock ({stock:g}) is below the Reorder Point
        ({reorder:g}) by {abs(diff):g} units."
    WORKED EXAMPLE TO MATCH EXACTLY: Current Stock=320, Reorder Point=700
    -> difference must equal -380.
  - IF "Current Stock" and "Max Stock Level" both present:
    for every row where Current Stock > Max Stock Level, emit finding
    finding_type="Overstock Review" with same pattern (difference = stock-max).
  - IF demand_df has item_col + "Demand" columns: merge on item_col, for
    rows where Demand > Current Stock emit finding_type=
    "Demand Coverage Risk".
  - IF prediction_df has item_col + "Predicted Demand": same pattern,
    finding_type="Predicted Demand Coverage Risk".
  - Any missing evidence source (demand/prediction/supplier/cost) must be
    silently skipped — never raise an error, never fabricate.
  - findings_df = pd.DataFrame(findings) or an empty DataFrame with columns
    ["item","finding_type","trigger_condition","explanation"] if no findings.
- Integration wrapper:
  - Add placeholder import-hook functions (_try_import_demand_df,
    _try_import_prediction_df, _try_import_supplier_df) that try to import
    Sujal's/Manthan's real modules (paths unknown yet — use
    modules.demand.get_demand_dataframe /
    modules.prediction.get_prediction_dataframe /
    modules.supplier.get_supplier_dataframe as placeholders, wrapped in
    try/except ImportError returning None) with a "# TODO: confirm real
    name" comment on each.
  - run_optimization(raw_df, item_col="Item") -> OptimizationResult: calls
    the import hooks, passes whatever it gets (or None) into
    find_optimization_issues. Must NEVER duplicate Sujal's/Manthan's
    calculation logic — only call their functions once real names are known.

============================================================
3. modules/recommendations.py
============================================================
- Converts optimization findings into full recommendation records for
  HUMAN REVIEW ONLY — never an instruction to act automatically.
- HUMAN_REVIEW_TEXT = "Human approval required. This is not an automated
  action."
- REQUIRED_FIELDS (every recommendation dict must contain exactly these
  keys): item, recommendation_type, trigger_condition, actual_values,
  comparison, reason, suggested_action, limitation, human_review.
- FORBIDDEN WORDING: never write "Order more inventory" or any direct
  command. ALWAYS use phrasing like "Recommended for review: ..." for
  suggested_action.
- Map each finding_type ("Reorder Review", "Overstock Review", "Demand
  Coverage Risk", "Predicted Demand Coverage Risk") to its own
  actual_values / comparison / reason / suggested_action text built from
  the finding's real numbers — not generic filler.
- RecommendationResult dataclass: available(bool), message(str|None),
  recommendations(list[dict]), recommendations_df(DataFrame|None).
- build_recommendations(findings) -> RecommendationResult: empty/None
  findings -> unavailable with message "No recommendations: no
  optimization findings were generated." (never fabricate a recommendation
  with no evidence).

============================================================
4. utils/export.py
============================================================
- export_to_csv(df) -> bytes|None: None if df is None/empty, else UTF-8
  CSV bytes via df.to_csv(index=False).
- Detect openpyxl availability at import time (EXCEL_AVAILABLE flag via
  try/except ImportError).
- export_to_excel(df) -> bytes|None: None if openpyxl unavailable or
  df None/empty; else .xlsx bytes via pd.ExcelWriter(engine="openpyxl").
- get_available_export_formats() -> list: always includes "csv"; adds
  "xlsx" only if EXCEL_AVAILABLE.
- Exported values must exactly match what the app displays. No fake rows.

============================================================
5. app.py (Streamlit)
============================================================
- st.set_page_config(page_title="Supply Chain Optimization System",
  layout="wide").
- Sidebar radio navigation with EXACTLY these pages in this order:
  Data Management, Dashboard, Inventory Analysis, Demand Analysis, Demand
  Prediction, Supplier Analysis, Cost Analysis, Optimization,
  Recommendations, Reporting.
- Session state: raw_df, dataset_name, _last_optimization_findings — all
  initialized to None. New CSV upload must reset
  _last_optimization_findings to None (clears stale state).
- Data Management page: CSV uploader, preview table, "Clear uploaded data"
  button, caption noting validation/cleaning is owned by teammates (TODO).
- Inventory Analysis / Demand Analysis / Demand Prediction / Supplier
  Analysis pages: show st.info("**{page}** is not yet available — this
  page is owned by Sujal/Manthan and has not been merged into `main`
  yet.") — DO NOT implement these pages or fake their logic.
- Dashboard: 4 KPI columns — Total Items, Total Stock (or "Unavailable"),
  Total Cost (from analyze_cost, or "Unavailable"), Items Needing Reorder
  Review (count of "Reorder Review" findings, or "Unavailable"). Never show
  an empty placeholder card — always a real number or "Unavailable".
- Cost Analysis / Optimization / Recommendations / Reporting pages: call
  the modules above, render totals/tables, show download buttons (CSV
  always, Excel if available) via a shared _download_buttons(df, base_name)
  helper.
- Auto-detect the item identifier column via a helper that tries "Item",
  "Item Name", "Product", "Product Name", "SKU", "Item ID", falling back
  to the first column.
- Reporting page aggregates: dataset summary, cost findings, optimization
  findings, recommendation findings (if any), and a "Limitations" section.

============================================================
6. Tests (tests/) — must ACTUALLY run and pass, not just exist
============================================================
- test_cost.py: all columns present; all columns missing (assert exact
  UNAVAILABLE_MESSAGE); partial columns; category-level grouping; empty
  DataFrame; None DataFrame.
- test_optimization.py: the exact 320/700/-380 worked example; no findings
  when stock healthy; overstock finding; missing inventory ->unavailable;
  demand coverage risk; predicted demand coverage risk; missing
  demand+prediction+supplier doesn't crash.
- test_recommendations.py: every required field present; forbidden wording
  absent ("order more inventory" must NOT appear, "recommended for review"
  MUST appear, case-insensitive check); empty/None findings -> unavailable;
  overstock wording check.
- test_export.py: CSV bytes contain the real values; empty/None -> None;
  "csv" always in available formats; Excel roundtrip only if openpyxl
  available.
- test_end_to_end.py: full pipeline UPLOAD(synthetic df)->cost->optimize->
  recommend->export, assert CSV bytes contain both an item name and "Human
  approval required"; missing prediction/supplier doesn't break it; missing
  cost columns -> unavailable with the exact message; empty filtered
  optimization results -> recommendations also unavailable (no fake rows).
- After writing all tests, RUN `python -m pytest tests/ -v` and show me the
  full output. Do not tell me it passes without actually running it.

============================================================
7. requirements.txt
============================================================
streamlit>=1.30
pandas>=2.0
openpyxl>=3.1
pytest>=7.4

============================================================
8. sample_data.csv
============================================================
Small synthetic CSV (6-8 rows) with columns: Item, Category, Current Stock,
Reorder Point, Max Stock Level, Unit Price, Purchase Cost, Holding Cost,
Transportation Cost — include at least one item clearly below Reorder Point
and one clearly above Max Stock Level, so the demo actually shows findings.

============================================================
9. README_ANSHU.md
============================================================
Document: what's implemented, expected column names, the exact
placeholder-import contract needed from Sujal/Manthan (module paths,
function names, expected DataFrame shape) before optimization.py's
run_optimization() wrapper can be wired to real data, and the out-of-scope
list below.

============================================================
INTEGRATION / DEPENDENCY RULES
============================================================
- Do NOT modify or reimplement Sujal's or Manthan's modules. Only import
  their public functions once known.
- Do NOT write the whole app.py as if all modules exist — use honest
  "not yet available" states for pages you don't own.
- Do NOT merge unfinished modules into app.py just to make it run.

============================================================
GIT WORKFLOW
============================================================
Branch: feature/anshu-integration
Before starting: git pull origin main
Commit message example: "feat: implement cost optimization recommendations
and reporting"
Then: git push origin feature/anshu-integration and open a PR.

============================================================
OUT OF SCOPE — do NOT add any of these
============================================================
Databases (MongoDB/MySQL/PostgreSQL/SQLite), Django, Flask, FastAPI, React,
automatic procurement, automatic supplier contact, supplier ranking/score,
fake AI, external production APIs, unnecessary animation, anything outside
this approved scope.

============================================================
SUCCESS CRITERIA
============================================================
Cost analysis works with partial/missing columns handled honestly;
optimization produces evidence-based findings only (no auto-decisions);
recommendations always require human review and never use command wording;
export matches displayed values exactly with no fake rows; dashboard shows
real KPIs or honest "Unavailable"; all 5 test files actually execute and
pass; README matches the real implementation with no unsupported feature
documented as done.
