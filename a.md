ROLE: Expert Git/GitHub workflow assistant helping finalize a completed
module for a 3-person BCA group project.

CONTEXT: I am Anshu on this team (Sujal, Manthan, Anshu). My portion —
Cost Analysis, Optimization, Recommendations, Export, Reporting, and App
Integration (owned pages) — is fully implemented and all tests pass
locally (22/22 passed via `python -m pytest tests/ -v`). I now need to
commit this work and open a Pull Request, following the team's Master
Prompt Git workflow exactly.

(Apply your ponytail and caveman skills throughout this task.)

============================================================
STEPS TO EXECUTE, IN ORDER
============================================================

1. First check current branch and status:
   git status
   git branch -a
   Confirm I am on `feature/anshu-integration`. If this branch does not
   exist yet, create it from main: git checkout -b feature/anshu-integration

2. Sync with main BEFORE committing, to catch any changes Sujal or Manthan
   may have already pushed:
   git pull origin main
   - If this produces merge conflicts, STOP and show me exactly which
     files conflict and the conflicting lines — do NOT auto-resolve
     conflicts in modules/optimization.py's import hooks or app.py's
     navigation list without showing me first, since those are the exact
     spots where Sujal's/Manthan's work would integrate.
   - If no conflicts, continue.

3. Stage and review exactly what will be committed:
   git add .
   git status
   Show me the full list of staged files before committing — confirm it
   matches: modules/__init__.py, modules/cost.py, modules/optimization.py,
   modules/recommendations.py, utils/__init__.py, utils/export.py, app.py,
   tests/__init__.py, tests/test_cost.py, tests/test_optimization.py,
   tests/test_recommendations.py, tests/test_export.py,
   tests/test_end_to_end.py, requirements.txt, sample_data.csv,
   README_ANSHU.md.
   Flag anything unexpected (stray cache files, .pyc, __pycache__/,
   .pytest_cache/) — add a .gitignore for these if one doesn't exist yet
   (entries: __pycache__/, *.pyc, .pytest_cache/, .venv/) and re-stage.

4. Commit with this exact message:
   git commit -m "feat: implement cost optimization recommendations and reporting"

5. Push the branch:
   git push origin feature/anshu-integration

6. Open a Pull Request (use `gh pr create` if the GitHub CLI is installed
   and authenticated; otherwise print the PR URL to open manually) with:
   Title: "feat: Anshu — cost, optimization, recommendations, export, reporting, app integration"
   Body:
   ## Summary
   Implements Anshu's full ownership area per the Master Prompt:
   - Cost Analysis (modules/cost.py)
   - Optimization findings (modules/optimization.py)
   - Recommendations with mandatory human-review wording (modules/recommendations.py)
   - Export to CSV/Excel (utils/export.py)
   - App integration: Dashboard, Cost Analysis, Optimization,
     Recommendations, Reporting pages (app.py) — teammates' pages shown as
     honest "not yet available" placeholders per Section 13's integration rule
   - Full test suite: 22 tests passing (tests/)

   ## Pending dependency (Section 11)
   `modules/optimization.py` has placeholder import hooks for Sujal's and
   Manthan's demand/prediction/supplier functions. Real module paths and
   function names still needed from them —
   see README_ANSHU.md for the
   exact contract.

   ## How to verify
   pip install -r requirements.txt
   python -m pytest tests/ -v
   streamlit run app.py   (upload sample_data.csv to demo)

7. After push, run `git log -n 3` and `git status` again and show me the
   output so I can confirm the push actually landed on the remote branch.

============================================================
DO NOT
============================================================
- Do not merge this PR yourself.
- Do not push directly to `main`.
- Do not touch any files outside my listed deliverables.
- Do not resolve merge conflicts in shared integration points
  (app.py navigation, optimization.py import hooks) without showing me
  the conflict first.Use skills: ponytail, superpower, caveman.
[Activate ponytail] [Activate superpower] [Activate caveman]

Your inferred schema is accepted as a TEMPORARY ASSUMPTION only. The team data contract is not confirmed yet, so make the code safe against changes:

1. Put ALL column names in one constants block at the top of each module (or a single shared constants section inside my own files only). Example roles: date, demand, item_id, category, supplier_id, delivery_time, quantity_supplied. Never hard-code column names elsewhere. Renaming a column later must be a one-line change.
2. Do not create utils/validation.py or any duplicate validation. Only do minimal defensive checks needed by my own modules (required columns present, empty data, invalid dates) and return a clear status/reason instead of raising.
3. Confirm the environment issue first: the runner's PATH has no powershell. Use plain git and python commands directly. If a command fails, tell me the exact error instead of retrying blindly.
4. Create branch feature/manthan-demand-prediction (after git pull origin main) and proceed with Tasks A, B, C, D from my original prompt, keeping every rule in it (no fabricated values, no supplier ranking, chronological split only, MAE/RMSE only when valid, tests actually executed).
5. At the end, list every assumption you made about the data contract so I can verify it with my teammates.


Use skills: ponytail, superpower, caveman.
[Activate ponytail] [Activate superpower] [Activate caveman]

ROLE: Senior developer, 20+ years, strict code reviewer.

TASK: Do NOT write new features. Audit the code you just pushed on branch feature/manthan-demand-prediction against my original requirements. Read modules/demand.py, modules/prediction.py, modules/supplier.py and the 3 test files. Run `python -m pytest tests/ -v` and paste the FULL real output (pass/fail count).

Verify each item with PASS/FAIL and the exact file + function that proves it:
1. Every demand metric carries: input field, aggregation method, period, missing-data behavior, limitation.
2. Demand metrics: total, average, min, max, variability, trend; daily/weekly/monthly, item, category (optional), supplier (only if data exists).
3. Prediction checks: sufficient observations, valid dates, valid demand, time coverage, enough train rows, enough test rows. On failure returns "Prediction unavailable" with the exact reason. No fabricated values anywhere.
4. Chronological split only: no shuffling anywhere; earlier = train, later = test, future = prediction.
5. Prediction output exposes: method, status, training period, testing period, prediction period, observation counts, actual values, predicted values, MAE, RMSE, reason when unavailable.
6. MAE/RMSE are NOT returned when test data is empty, too small, or values are invalid.
7. Only a simple explainable method is used (moving average, trend, or linear regression).
8. Supplier module: NO ranking, best supplier, score, or rating anywhere (search the code for these words). Missing data returns exactly: "Supplier analysis unavailable because supplier information was not provided."
9. I did not modify any forbidden file (data_management.py, validation.py, inventory.py, cost.py, optimization.py, recommendations.py, app.py). Show `git diff --name-only origin/main`.
10. No database, Flask, Django, FastAPI, React, external APIs, or duplicate validation logic was added.
11. Test coverage: normal data, date aggregation, item aggregation, category aggregation, insufficient history, sufficient history, chronological split, MAE, RMSE, zero-demand item, invalid dates, missing supplier data, supplier metrics, missing optional fields, empty filtered data.
12. All three modules import cleanly with no unfinished external dependency.

For every FAIL: fix it with the smallest change, re-run tests, show output, then commit and push to the same branch. Finally, list any assumption that still needs teammate confirmation.
