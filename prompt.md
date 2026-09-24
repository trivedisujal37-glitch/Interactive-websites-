Role: You are implementing the "Data & Inventory Module" for a BCA final-year academic project called "Supply Chain Optimization" (Python + Streamlit, CSV/Excel-based, no database). You are one of 3 team members (Sujal, Manthan, Anshu). You own ONLY the files listed below — do not touch or redesign app.py, requirements.txt, README.md, or teammates' modules (demand.py, prediction.py, supplier.py, cost.py, optimization.py, recommendations.py). Do not redesign the project architecture or add features outside this scope.

FILES TO CREATE/IMPLEMENT:
1. modules/data_management.py
2. utils/validation.py
3. modules/inventory.py
4. tests/test_data_management.py
5. tests/test_validation.py
6. tests/test_inventory.py
(Optionally: supporting documentation for your own modules.)

=== 1. modules/data_management.py ===
- CSV reading (Excel reading too if Excel support is enabled)
- Column normalization (case/whitespace-insensitive matching)
- Alias mapping to standard logical fields — required: item identifier, date, demand measure, current stock; optional: item name, category, supplier ID, delivery time, quantity supplied, unit price, purchase cost, holding cost, transportation cost
- Data cleaning (missing values, duplicates, type coercion)
- Data transformation into a clean, analysis-ready DataFrame
- Cleaning summary (rows before/after, what was fixed/dropped)
- Original vs cleaned row tracking
- Preserve unknown columns instead of dropping them
- Never hard-code company/product/supplier names or invent business data not present in the file

=== 2. utils/validation.py ===
- File validation (exists, readable) + extension validation (.csv, .xlsx only)
- Empty/corrupt file handling with clear errors
- Required-column validation, optional-column detection, unknown-column handling (keep, don't error)
- Duplicate/conflicting alias detection
- Data-type validation, null detection, invalid-date detection
- Negative demand/stock/lead-time validation, general numeric validation
- Handling for very small (1-row) or empty datasets
- Return clear, human-readable validation messages, not just booleans

=== 3. modules/inventory.py ===
Per item, compute:
- Average demand, safety stock
- Reorder point — use this exact fallback formula unless an official one is supplied, and NEVER silently change it:
  Reorder Point = (Average Demand × Lead Time) + Safety Stock
- Current stock, stock gap (current stock − reorder point)
- Inventory status, one of: Low Stock, Overstock, Priority Review, Review Required, Sufficient

Do NOT generate recommendations — that module belongs to a teammate (Anshu). Output must expose: item/entity, average demand, lead time (when available), safety stock, reorder point, current stock, stock gap, inventory status — so dashboard/optimization/recommendation/reporting code can consume it.

=== 4. DEPENDENCY RULE ===
Your code must not depend on unfinished code from Manthan or Anshu. You may use Pandas, NumPy, and other approved project libraries. If another module isn't ready, use a clearly documented interface/contract rather than copying their code. Never duplicate another member's module.

=== 5. Tests ===
Cover and ACTUALLY RUN (don't just write test files and claim pass):
CSV upload, Excel upload (if implemented), missing required column, missing optional columns, alias mapping, conflicting aliases, duplicate records, missing values, invalid dates, negative numeric values, non-numeric values, zero-demand item, low-stock item, overstock item, high-demand/low-stock item, empty dataset, one-row dataset, zero-row-after-cleaning dataset, inventory formula correctness.

For each test report: test name, command run, expected result, actual result, status — using ONLY: PASS, PARTIAL, CONDITIONAL, NOT VERIFIED, BLOCKED. Never mark PASS without actual run evidence.

HARD CONSTRAINTS:
- No database of any kind (MongoDB/MySQL/PostgreSQL/SQLite)
- No Django/Flask/FastAPI/React/Node backend
- No automatic purchasing, supplier ranking/scoring, external APIs, fake AI, or unnecessary animation
- Expose clear, documented functions (docstrings, predictable inputs/outputs, explicit error handling) — do not hide calculations inside Streamlit UI code

PROJECT PIPELINE CONTEXT: The full app follows UPLOAD → VALIDATE → CLEAN → TRANSFORM → ANALYZE → PREDICT → OPTIMIZE → RECOMMEND → EXPORT. Your responsibility covers VALIDATE → CLEAN → INVENTORY ANALYZE only.

GIT WORKFLOW: Never work directly on main and never force-push shared branches. Create/use branch feature/sujal-data-inventory (pull main first). Commit with a message like "feat: implement data validation and inventory modules", push to that branch, open a PR — do not merge your own PR unless the team agrees.

SUCCESS CONDITION (your work is ready for integration only when ALL of these are true):
- Modules import successfully and functions are defined
- Validation, cleaning, and inventory calculations work correctly
- Edge cases are handled
- Tests actually run (not just written)
- No hard-coded business assumptions exist
- Outputs follow the team data contract
- Your branch can be merged without modifying another member's work

FINAL REPORT — after finishing, provide:
1. Files created/modified
2. Functions created
3. Dependencies added, if any
4. Tests executed and their results
5. Known limitations
6. Integration requirements for other members
7. Git commit hash
8. Status of each module (data_management, validation, inventory) using PASS/PARTIAL/CONDITIONAL/NOT VERIFIED/BLOCKED
Do not say "complete" unless direct evidence exists.

ponytail caveman