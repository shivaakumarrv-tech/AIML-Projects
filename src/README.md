# Customer Intelligence & Support Copilot — corrected local production kit

This kit is for **local Windows use**. It sets up a Python virtual environment, installs project and Streamlit dependencies, generates the synthetic CSV datasets and policy documents when needed, and starts the browser walkthrough.

## 1. Important correction for your folder layout

The supplied `generate_data.py` originally used paths relative to whichever folder the command prompt happened to be in, and wrote policy documents only to `data/policies`. The corrected generator now anchors all paths to the folder containing `generate_data.py`, so it works even if launched from another current directory.

It creates:

- CSV data in `data/raw/`: `customers.csv`, `products.csv`, `orders.csv`, `tickets.csv`, and `policy_eval.csv`.
- Policy text files in **both** `data/policies/` and `notebooks/data/policies/`.

The duplicate policy output is intentional: your existing `src/policy_rag.py` and `src/refund_agent.py` read from `data/policies/`, while the notebook-side folder you requested is also populated. The two locations contain the same generated policy documents.

## 2. Required folder structure

Keep the whole kit together in your project root. Merge it with your existing project; do not copy only `app.py`.

```text
Customer_Intelligence_Support_Copilot/
├── app.py
├── START_PROJECT.bat
├── generate_data.py
├── mock_llm.py
├── requirements.txt
├── requirements_frontend.txt
├── .venv/                         # created automatically
├── src/
│   ├── __init__.py
│   ├── data_pipeline.py
│   ├── customer_models.py
│   ├── triage.py
│   ├── policy_rag.py
│   ├── refund_agent.py
│   └── churn_analysis.py
├── data/
│   ├── raw/                       # generated automatically
│   ├── clean/                     # created by cleaning stage
│   └── policies/                  # generated automatically; read by app modules
├── notebooks/
│   └── data/
│       └── policies/              # generated automatically; notebook-side copy
├── outputs/                       # created by project stages
└── state/                          # created by refund workflow
```

The kit includes the uploaded `generate_data.py`, `mock_llm.py`, and original `requirements.txt`, along with the supplied project modules. Preserve any additional files your original project needs.

## 3. One-click startup

1. Install Python 3.10+ on Windows and enable **Add Python to PATH** during installation.
2. Extract/merge this folder into the project root.
3. Double-click `START_PROJECT.bat`.
4. On first launch it creates `.venv`, upgrades pip, installs `requirements.txt` and `requirements_frontend.txt`, checks the raw datasets, and runs `generate_data.py` if any required CSV is missing. If raw data exists but policy files are missing, it also runs the generator.
5. Streamlit starts at `http://localhost:8501`. Your default browser should open; if not, open Chrome/Edge and enter that address.
6. Keep the command window open while using the browser. Press `Ctrl+C` in that window to stop Streamlit.

Subsequent launches reuse `.venv` and skip data generation if all expected raw CSV files and policy files exist. To recreate the sample data intentionally, remove the generated CSVs and policy `.txt` files first, then run the batch file again, or use the app's Generate sample data button.

## 4. Why you saw PermissionError on orders.csv

The generator opens `data/raw/orders.csv` in write mode because it recreates the synthetic dataset. Windows can deny this if:

- `orders.csv` is open in Excel, Notepad, a CSV previewer, or another process;
- the file has the Windows **Read-only** attribute;
- the project folder is under a protected location or your account lacks Modify permission;
- `orders.csv` is actually a folder, not a file;
- antivirus, sync software, or backup software temporarily locks the file.

Before retrying:

1. Close Excel and any program that may have `orders.csv` open.
2. In File Explorer, right-click `data/raw/orders.csv` → Properties → clear **Read-only** if selected.
3. Ensure your Windows account has Modify permission on the project folder. Prefer a writable location such as `D:\AI\Projects\Customer_Intelligence_Support_Copilot` rather than `Program Files`.
4. Check that `data/raw/orders.csv` is a file, not a directory.
5. Double-click `START_PROJECT.bat` again.

The batch file attempts to clear the read-only attribute on generated CSV and policy files. It cannot unlock a file that another program currently holds open. The updated generator prints a more helpful error naming the exact file and suggesting these checks.

## 5. Browser walkthrough

Use the sidebar in the browser. Recommended order:

1. **Project home** — check readiness and optionally generate sample data.
2. **Data audit** — inspect source data quality.
3. **Clean & validate** — create cleaned files/database and validate them.
4. **Customer segments** — run RFM and K-means segmentation.
5. **Lapse prediction** — build and evaluate the lapse model.
6. **Support ticket triage** — classify tickets, review routes, redactions and token summary.
7. **Policy assistant** — ask questions grounded in generated policy text files.
8. **Refund workflow** — run the bounded local demonstration; it does not issue real payments.
9. **Churn analysis** — run the churn analysis module.
10. **Project outputs** — review generated files.

Each stage is started with its on-screen button. Run the stages in order because later stages depend on data created by earlier ones.

## 6. Are app.py and requirements_frontend.txt alone enough?

No. They are the UI and its extra dependencies, not the full application. You also need `src/`, `generate_data.py`, `mock_llm.py`, the original `requirements.txt`, and any other original project assets. This kit includes those uploaded files and a Windows startup script.

## 7. Local vs public deployment

`localhost:8501` is available only on the computer running Streamlit. This batch file is not a public internet deployment. For a shared/public production deployment, configure a server or managed hosting, authentication, authorization, secrets, network controls, data retention and backups before using real customer data.

## 8. Troubleshooting

- **Python not found:** install Python 3.10+ and add it to PATH.
- **PermissionError for orders.csv:** close programs using the file, clear Read-only, verify folder Modify permission, and retry.
- **ModuleNotFoundError:** verify the complete `src/` folder and root-level `mock_llm.py` are present; run `START_PROJECT.bat` to install dependencies.
- **No policies found:** run `generate_data.py` from the project root or click Generate sample data; check both `data/policies/` and `notebooks/data/policies/`.
- **Browser does not open:** manually visit `http://localhost:8501` while the command window is running.
- **Port 8501 in use:** stop the other Streamlit process or change `--server.port 8501` in `START_PROJECT.bat` and use the corresponding URL.

This is a teaching/demo project. Validate all workflows with your actual deployment environment before production use.
