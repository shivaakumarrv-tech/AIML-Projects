# Customer Intelligence & Support Copilot 

This kit is for **local Windows use**. It sets up a Python virtual environment, installs project and Streamlit dependencies, generates the synthetic CSV datasets and policy documents when needed, and starts the browser walkthrough.

## 1. Required folder structure

Keep the whole kit together in your project root. 

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


## 2. One-click startup

1. Install Python 3.10+ on Windows and enable **Add Python to PATH** during installation.
2. Extract/merge this folder into the project root.
3. Double-click `START_PROJECT.bat`.
4. On first launch it creates `.venv`, upgrades pip, installs `requirements.txt` and `requirements_frontend.txt`, checks the raw datasets, and runs `generate_data.py` if any required CSV is missing. If raw data exists but policy files are missing, it also runs the generator.
5. Streamlit starts at `http://localhost:8501`. Your default browser should open; if not, open Chrome/Edge and enter that address.
6. Keep the command window open while using the browser. Press `Ctrl+C` in that window to stop Streamlit.

Subsequent launches reuse `.venv` and skip data generation if all expected raw CSV files and policy files exist. To recreate the sample data intentionally, remove the generated CSVs and policy `.txt` files first, then run the batch file again, or use the app's Generate sample data button.

## 3. Browser walkthrough

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

## 4. Local vs public deployment

`localhost:8501` is available only on the computer running Streamlit. This batch file is not a public internet deployment. For a shared/public production deployment, configure a server or managed hosting, authentication, authorization, secrets, network controls, data retention and backups before using real customer data.

## 5. Troubleshooting

Included basic troubleshooting steps durinig deployment

- **Python not found:** install Python 3.10+ and add it to PATH.
- **PermissionError for orders.csv:** close programs using the file, clear Read-only, verify folder Modify permission, and retry.
- **ModuleNotFoundError:** verify the complete `src/` folder and root-level `mock_llm.py` are present; run `START_PROJECT.bat` to install dependencies.
- **No policies found:** run `generate_data.py` from the project root or click Generate sample data; check both `data/policies/` and `notebooks/data/policies/`.
- **Browser does not open:** manually visit `http://localhost:8501` while the command window is running.
- **Port 8501 in use:** stop the other Streamlit process or change `--server.port 8501` in `START_PROJECT.bat` and use the corresponding URL.

This is a teaching/demo project. Validate all workflows with your actual deployment environment before production use.


### Churn charts in Streamlit

When you run **Churn analysis** from the sidebar, the app displays the charts produced by the churn module. PNG files are saved in `outputs/churn/charts/`:

- Customer churn distribution
- Churn rate by city
- Churn rate by age group
- Revenue by product category
- Predictive model confusion matrix (when the model has enough data to train)
- Top 15 churn predictors (when the model has enough data to train)

The predictive-model charts appear only when the training data contains enough examples from both churn classes.
