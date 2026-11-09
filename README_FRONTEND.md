# Customer Intelligence & Support Copilot — Browser Front Page

This is a Streamlit front page for the existing project. It calls the existing Python modules; it does not replace their algorithms.

## 1. Arrange your project folders

Keep your existing project files and arrange them like this:

```text
Customer_Intelligence_Support_Copilot/
├── app.py
├── requirements_frontend.txt
├── src/
│   ├── __init__.py
│   ├── data_pipeline.py
│   ├── customer_models.py
│   ├── triage.py
│   ├── policy_rag.py
│   ├── refund_agent.py
│   └── churn_analysis.py
├── mock_llm.py
├── data/
│   ├── raw/
│   │   ├── customers.csv
│   │   ├── orders.csv
│   │   ├── products.csv
│   │   └── tickets.csv
│   ├── policies/
│   │   └── *.txt
│   └── clean/
└── outputs/
```

Copy the six uploaded Python files into `src/`. Rename `churn_analysis(2).py` to `churn_analysis.py`.

**Important:** The six source files provided in this chat do not include `mock_llm.py`, the raw/clean CSV data, or the policy text documents. Your project notebook refers to `mock_llm.py` and a data-generation script. Keep your existing copies of these files in the locations above. The ticket triage, policy assistant and refund workflow need `mock_llm.py`; the policy assistant and refund workflow also need policy `.txt` files. The data audit/cleaning stages need the raw CSVs.

## 2. Install dependencies

Open Command Prompt or PowerShell in the project root and run:

```bash
python -m venv .venv
```

Activate it:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt**
```bat
.venv\Scripts\activate.bat
```

Install the packages:

```bash
pip install -r requirements_frontend.txt
```

If your project already has a `requirements.txt`, you can install that instead, then install Streamlit:

```bash
pip install streamlit
```

## 3. Start the browser app

From the same project root:

```bash
streamlit run app.py
```

Streamlit normally opens the app in your default browser. If it does not, copy the `Local URL` shown in the terminal (usually `http://localhost:8501`) into Chrome, Edge, Firefox or another browser.

## 4. Follow the walkthrough

Use the left-hand menu in this order:

1. **Data audit** — inspect the raw data.
2. **Clean & validate** — create `data/clean/` and `data/instamart.db`.
3. **Customer segments** — run RFM and K-means.
4. **Lapse prediction** — train and evaluate the existing lapse model.
5. **Support ticket triage** — classify and route tickets.
6. **Policy assistant** — ask questions against the policy text files.
7. **Refund workflow** — try the refund-support agent with an order ID.
8. **Churn analysis** — run the separate churn analysis and review its reports.
9. **Project outputs** — preview and download generated CSV reports.

Run the cleaning stage before the analysis stages. Run customer segmentation before ticket triage because triage uses the customer segment output when it is available.

## 5. Open it from another device/browser

- **Same computer:** use the Local URL in any installed browser.
- **Same Wi-Fi/network:** start Streamlit with `streamlit run app.py --server.address 0.0.0.0`, then open `http://<computer-LAN-IP>:8501` on another device. The computer firewall may need to allow port 8501. Do this only on a trusted network.
- **From anywhere on the internet:** deploy the project to a hosting service such as Streamlit Community Cloud or another server. Keep customer data and secrets out of a public repository. Use synthetic/demo data for public demonstrations and configure access controls before exposing private data.

“Runs in a browser” does not mean the app is automatically public on the internet. Local mode is accessible only where the computer/network permits it.

## Notes and limitations

- The app calls your current `src` modules; it does not rewrite them.
- The refund module writes to a local JSONL ledger. It does not send money or call a payment gateway.
- The uploaded `churn_analysis(2).py` file is expected to be renamed to `src/churn_analysis.py`.
- The uploaded source set does not contain `mock_llm.py`, raw data, policy text files or a data generator. Those existing project assets must be supplied for the corresponding stages.
- If a module raises an error, the app shows the error and technical traceback so you can identify the missing dependency or input file.
