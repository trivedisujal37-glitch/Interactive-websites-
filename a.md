Use skills: ponytail, superpower, caveman.
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