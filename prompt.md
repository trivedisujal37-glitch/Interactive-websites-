Use skills: ponytail, superpower, caveman.
[Activate ponytail] [Activate superpower] [Activate caveman]
Apply all three on every step of this task: ponytail for structured step-by-step execution, superpower for deep, careful engineering, caveman for minimal, terse, no-fluff output and code.

ROLE: Act as a senior developer with 20+ years of experience in Python, data analysis and clean, testable design.

CONTEXT: BCA final-year project "Supply Chain Optimization System", 3-person team (Sujal, Manthan, Anshu). I am Manthan. I own the Demand, Prediction and Supplier analysis layer. Deadline: 3 Jan. Follow the team's Master Prompt and data contract. Do NOT wait for Sujal's code; develop against the documented data contract using small sample DataFrames.

FIRST: Inspect the repo. Read app.py, modules/, utils/ and any Master Prompt / README / data contract. Do not modify anything yet. Tell me the data contract (column names, types, normalized format) you found. If something is unclear, ask me before assuming.

GIT: Run `git pull origin main`, then create/switch to branch `feature/manthan-demand-prediction`.

FILES I MAY MODIFY: modules/demand.py, modules/prediction.py, modules/supplier.py, tests/test_demand.py, tests/test_prediction.py, tests/test_supplier.py
FILES I MUST NOT TOUCH: modules/data_management.py, utils/validation.py, modules/inventory.py, modules/cost.py, modules/optimization.py, modules/recommendations.py. Do not redesign app.py. Do not copy Sujal's implementation. Do not write duplicate validation functions that belong to utils/validation.py. My modules accept clean/normalized data.

GLOBAL RULES: Never invent or fabricate values. Every output must contain real calculated values only. Keep it simple and explainable, no fake AI, no complex ML.
DO NOT ADD: database, MongoDB, SQL, Django, Flask, FastAPI, React, automatic procurement, supplier ranking/best supplier/score/rating, complex ML without justification, external production APIs, out-of-scope features.

TASK A - modules/demand.py (data-supported analysis only):
Metrics: total, average, min, max demand, demand variability, demand trend.
Aggregations: daily, weekly, monthly, by item, by category (only when available), by date, by supplier (only when supplier data exists).
Every metric result must carry: input field, aggregation method, period, missing-data behavior, limitation.
Handle: zero-demand items, missing optional fields, empty filtered data (return a clear status/message, do not crash).

TASK B - modules/prediction.py (CONDITIONAL prediction):
Before predicting, check: sufficient observations, valid dates, valid demand values, reasonable time coverage, enough training rows, enough testing rows.
If any check fails: return status "Prediction unavailable" with the exact reason. Never fabricate predictions.
Method: use the documented method if one exists in the repo; otherwise a simple explainable one (moving average, time-based trend, or linear regression). No complex ML without documented justification.
Leakage prevention: NEVER shuffle chronological data. Earlier records = training, later = testing, future period = prediction.
Expose: method used, status, training period, testing period, prediction period, observation counts, actual values (if available), predicted values (if available), reason when unavailable.
Evaluation: compute MAE and RMSE only when valid prediction exists. Do NOT return/display them when test data is empty, too small, or actual/predicted values are invalid.

TASK C - modules/supplier.py (evidence-based only):
Analyze only what data supports: supplier ID, average delivery time, total quantity supplied, supply consistency, supplier demand/supply patterns.
FORBIDDEN: supplier ranking, best supplier, supplier score, supplier rating.
If supplier data is missing, return exactly: "Supplier analysis unavailable because supplier information was not provided."

DOWNSTREAM CONTRACT: Outputs must be usable by Optimization, Recommendations, Dashboard and Reporting. Return clear, structured outputs (consistent dict/DataFrame shape with a status field), matching the team contract.

TASK D - Tests (write AND actually execute them with pytest, show real results):
tests/test_demand.py, tests/test_prediction.py, tests/test_supplier.py covering at minimum: normal demand data, date aggregation, item aggregation, category aggregation, insufficient prediction history, sufficient prediction history, chronological train/test split, MAE, RMSE, zero-demand item, invalid dates, missing supplier data, supplier metrics, missing optional fields, empty filtered data.

WORKFLOW: Plan first (short), implement one module at a time, run its tests, fix failures before moving on. Then run the full test suite and confirm all 3 modules import correctly with no unfinished external dependency.

DONE WHEN: all 3 modules import; demand analysis works; prediction conditions are checked; no chronological leakage; MAE/RMSE only when valid; supplier analysis is data-dependent and handles missing data; tests pass when actually run; outputs follow the team contract.

FINISH: Show git status, then commit with message "feat: implement demand prediction and supplier analysis", push to origin feature/manthan-demand-prediction, and tell me to open a Pull Request. Do not push to main.