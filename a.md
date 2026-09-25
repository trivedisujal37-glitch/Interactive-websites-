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
  the conflict first.