from pathlib import Path
import sys
import io
import contextlib
import traceback
import subprocess
import sqlite3
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="Customer Intelligence & Support Copilot",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------- Styling ---------------------------
st.markdown("""
<style>
:root { --ink:#172033; --muted:#667085; --line:#e7eaf0; --accent:#3157d5; }
.block-container {padding-top: 1.7rem; padding-bottom: 3rem; max-width: 1440px;}
.hero {
  padding: 2.2rem 2.4rem; border-radius: 22px;
  background: linear-gradient(125deg,#172554 0%,#263f83 52%,#4774bd 100%);
  color: white; margin-bottom: 1.2rem;
}
.hero h1 {font-size:2.25rem; line-height:1.15; margin:0 0 .6rem 0; color:white;}
.hero p {font-size:1.04rem; opacity:.9; max-width:850px; margin:0;}
.eyebrow {text-transform:uppercase; letter-spacing:.13em; font-size:.72rem; font-weight:700; opacity:.8;}
.step-card {
  border:1px solid var(--line); border-radius:15px; padding:1rem 1.1rem;
  background: white; min-height:120px;
}
.step-number {font-size:.78rem; font-weight:700; color:#3157d5; letter-spacing:.08em;}
.step-title {font-size:1.05rem; font-weight:700; margin:.3rem 0;}
.step-copy {color:#667085; font-size:.9rem;}
.small-note {color:#667085; font-size:.85rem;}
div[data-testid="stMetric"] {border:1px solid #e7eaf0; padding:12px 14px; border-radius:13px;}
</style>
""", unsafe_allow_html=True)

# --------------------------- Helpers ---------------------------
def exists(rel):
    return (ROOT / rel).exists()

def import_module(name):
    import importlib
    return importlib.import_module(name)

def capture_call(fn, *args, **kwargs):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        result = fn(*args, **kwargs)
    return result, buf.getvalue()

def data_status():
    required = ["customers.csv", "orders.csv", "products.csv"]
    clean = ROOT / "data" / "clean"
    raw = ROOT / "data" / "raw"
    return {
        "raw": raw,
        "clean": clean,
        "raw_files": {f: (raw / f).exists() for f in required},
        "clean_files": {f: (clean / f).exists() for f in required},
        "mock_llm": (ROOT / "mock_llm.py").exists(),
        "policies": list((ROOT / "data" / "policies").glob("*.txt")) if (ROOT / "data" / "policies").exists() else [],
        "tickets_raw": (raw / "tickets.csv").exists(),
    }

def show_exception(err):
    st.error(f"{type(err).__name__}: {err}")
    with st.expander("Technical details"):
        st.code(traceback.format_exc())

def section_header(kicker, heading, description):
    st.markdown(f"<div class='eyebrow'>{kicker}</div>", unsafe_allow_html=True)
    st.title(heading)
    st.write(description)

def render_table(value, height=340):
    if isinstance(value, pd.DataFrame):
        st.dataframe(value, use_container_width=True, height=height)
    else:
        st.write(value)

# --------------------------- Sidebar ---------------------------
st.sidebar.markdown("## 🛍️ Project menu")
page = st.sidebar.radio(
    "Navigate",
    [
        "Project home",
        "1 · Data audit",
        "2 · Clean & validate",
        "3 · Customer segments",
        "4 · Lapse prediction",
        "5 · Support ticket triage",
        "6 · Policy assistant",
        "7 · Refund workflow",
        "8 · Churn analysis",
        "Project outputs",
    ],
)
st.sidebar.divider()
st.sidebar.caption("Customer Intelligence & Support Copilot")
st.sidebar.caption("Browser-based project walkthrough")

status = data_status()

# --------------------------- Home ---------------------------
if page == "Project home":
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">End-to-end customer analytics demonstration</div>
      <h1>Customer Intelligence<br>& Support Copilot</h1>
      <p>Explore customer behaviour, identify customers who may lapse, organise support requests,
      search company policies and walk through a controlled refund-support process — all from one browser page.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Project stages", "8")
    c2.metric("Data source", "Local CSV")
    c3.metric("Database", "SQLite")
    c4.metric("Interface", "Browser")

    st.subheader("Welcome to the project")
    st.write(
        "This front page brings the Python modules in your `src` folder together in a guided interface. "
        "Use the menu on the left to run each stage in sequence, view its results and understand what it does."
    )

    st.subheader("Recommended walkthrough")
    cards = [
        ("01", "Check the source data", "Review missing values, duplicates and unusual values before processing."),
        ("02", "Prepare the data", "Clean customer and order records, save clean CSV files and build the SQLite database."),
        ("03", "Understand customers", "Create RFM measures and group customers using K-means clustering."),
        ("04", "Estimate lapse risk", "Train and evaluate the existing customer lapse model."),
        ("05", "Route support tickets", "Redact selected personal details, classify tickets and route exceptions for review."),
        ("06", "Ask policy questions", "Retrieve relevant passages from the policy text files and produce a grounded answer."),
        ("07", "Try the refund workflow", "Look up an order and run the project's bounded refund-support agent."),
        ("08", "Explore churn", "Review descriptive churn measures and the separate Random Forest churn model."),
    ]
    for start in range(0, len(cards), 2):
        cols = st.columns(2)
        for col, item in zip(cols, cards[start:start+2]):
            with col:
                st.markdown(
                    f"<div class='step-card'><div class='step-number'>STEP {item[0]}</div>"
                    f"<div class='step-title'>{item[1]}</div><div class='step-copy'>{item[2]}</div></div>",
                    unsafe_allow_html=True,
                )
        st.write("")

    st.subheader("Project readiness")
    ready_items = [
        ("src/data_pipeline.py", exists("src/data_pipeline.py")),
        ("src/customer_models.py", exists("src/customer_models.py")),
        ("src/triage.py", exists("src/triage.py")),
        ("src/policy_rag.py", exists("src/policy_rag.py")),
        ("src/refund_agent.py", exists("src/refund_agent.py")),
        ("src/churn_analysis.py", exists("src/churn_analysis.py")),
        ("mock_llm.py", status["mock_llm"]),
        ("data/raw/customers.csv", status["raw_files"]["customers.csv"]),
        ("data/raw/orders.csv", status["raw_files"]["orders.csv"]),
        ("data/raw/products.csv", status["raw_files"]["products.csv"]),
    ]
    for label, ok in ready_items:
        st.write(("✅ " if ok else "⚠️ ") + label)
    if not status["mock_llm"]:
        st.warning("The uploaded files do not include `mock_llm.py`. Ticket triage, policy answers and the refund agent import it. Add your existing project copy before using those stages.")
    if not all(status["raw_files"].values()):
        st.info("The raw customer, order and product CSV files are not all present. Add them under `data/raw/` before running the audit and cleaning stages.")

    st.info("This app runs your existing Python modules. It does not replace or rewrite the code in `src/`.")

    st.subheader("Create or recreate sample data")
    generator = ROOT / "generate_data.py"
    if generator.is_file():
        st.caption(
            "This runs generate_data.py from the project root and writes synthetic CSV files "
            "to data/raw/ (and policy documents to data/policies/). Existing files with the "
            "same names will be overwritten."
        )

        if st.button("Generate sample data", type="secondary", key="generate_sample_data"):
            # Clear the previous result so the latest run is always shown.
            st.session_state.pop("sample_data_result", None)
            st.session_state.pop("sample_data_error", None)
            try:
                with st.spinner("Generating sample datasets... please wait"):
                    completed = subprocess.run(
                        [sys.executable, str(generator)],
                        cwd=str(ROOT),
                        capture_output=True,
                        text=True,
                        timeout=180,
                        check=False,
                    )

                run_output = (completed.stdout or "").strip()
                run_error = (completed.stderr or "").strip()
                if completed.returncode == 0:
                    expected_files = [
                        ROOT / "data" / "raw" / "customers.csv",
                        ROOT / "data" / "raw" / "orders.csv",
                        ROOT / "data" / "raw" / "products.csv",
                        ROOT / "data" / "raw" / "tickets.csv",
                        ROOT / "data" / "raw" / "policy_eval.csv",
                    ]
                    created = [str(f.relative_to(ROOT)) for f in expected_files if f.is_file()]
                    missing = [str(f.relative_to(ROOT)) for f in expected_files if not f.is_file()]
                    st.session_state["sample_data_result"] = {
                        "stdout": run_output,
                        "stderr": run_error,
                        "created": created,
                        "missing": missing,
                    }
                else:
                    st.session_state["sample_data_error"] = {
                        "returncode": completed.returncode,
                        "stdout": run_output,
                        "stderr": run_error,
                    }
            except subprocess.TimeoutExpired as e:
                st.session_state["sample_data_error"] = {
                    "returncode": "timeout",
                    "stdout": e.stdout or "",
                    "stderr": "The data-generation script exceeded 180 seconds and was stopped.",
                }
            except Exception:
                st.session_state["sample_data_error"] = {
                    "returncode": "exception",
                    "stdout": "",
                    "stderr": traceback.format_exc(),
                }

        # Render the saved result on this run and on later Streamlit reruns.
        result = st.session_state.get("sample_data_result")
        if result:
            if result["missing"]:
                st.warning("The generator finished, but some expected files were not found.")
            else:
                st.success("Sample data generated successfully. The raw datasets have been created or recreated.")
            st.write("Files found:", ", ".join(result["created"]) or "None")
            if result["missing"]:
                st.error("Missing files: " + ", ".join(result["missing"]))
            if result["stdout"]:
                st.text("Generator output")
                st.code(result["stdout"])
            if result["stderr"]:
                with st.expander("Generator warnings"):
                    st.code(result["stderr"])

        error = st.session_state.get("sample_data_error")
        if error:
            st.error(f"Data generation failed (status: {error['returncode']}).")
            if error["stdout"]:
                st.code(error["stdout"])
            if error["stderr"]:
                st.code(error["stderr"])
    else:
        st.warning(
            "generate_data.py was not found in the project root. Place it beside app.py "
            "to enable sample-data generation."
        )

# --------------------------- Audit ---------------------------
elif page == "1 · Data audit":
    section_header("STEP 01", "Data audit", "Inspect the original customer, product and order files before changing them.")
    st.write("The audit prints each table's shape and data types, then reports common data-quality checks.")
    if st.button("Run data audit", type="primary"):
        try:
            module = import_module("src.data_pipeline")
            _, output = capture_call(module.audit)
            st.session_state["audit_output"] = output
            st.success("Audit completed.")
        except Exception as e:
            show_exception(e)
    if "audit_output" in st.session_state:
        st.code(st.session_state["audit_output"])

# --------------------------- Clean & validate ---------------------------
elif page == "2 · Clean & validate":
    section_header("STEP 02", "Clean and validate data", "Prepare consistent datasets and store them in the SQLite database.")
    st.warning("This step writes files to `data/clean/` and replaces the project's SQLite tables in `data/instamart.db`.")
    a, b = st.columns(2)
    with a:
        if st.button("Run cleaning", type="primary"):
            try:
                module = import_module("src.data_pipeline")
                result, output = capture_call(module.clean_data)
                st.session_state["clean_output"] = output
                st.session_state["clean_result"] = result
                st.success("Cleaning completed.")
            except Exception as e:
                show_exception(e)
    with b:
        if st.button("Run validation"):
            try:
                module = import_module("src.data_pipeline")
                _, output = capture_call(module.validate)
                st.session_state["validate_output"] = output
                st.success("Validation completed.")
            except Exception as e:
                show_exception(e)
    if "clean_result" in st.session_state:
        st.subheader("Cleaned data preview")
        for name, frame in st.session_state["clean_result"].items():
            with st.expander(f"{name.title()} · {len(frame):,} rows"):
                st.dataframe(frame.head(20), use_container_width=True)
    if "clean_output" in st.session_state:
        st.code(st.session_state["clean_output"])
    if "validate_output" in st.session_state:
        st.code(st.session_state["validate_output"])

# --------------------------- Segmentation ---------------------------
elif page == "3 · Customer segments":
    section_header("STEP 03", "Customer segments", "Compare customers using recency, frequency and monetary value.")
    st.write("RFM means how recently a customer ordered, how often they ordered and how much they spent.")
    k = st.slider("Number of customer groups (K)", min_value=2, max_value=8, value=4)
    if st.button("Run customer segmentation", type="primary"):
        try:
            module = import_module("src.customer_models")
            (rfm, diagnostics, profile, pca), output = capture_call(module.rfm_and_segments, k=k)
            st.session_state["rfm"] = rfm
            st.session_state["kdiag"] = diagnostics
            st.session_state["profile"] = profile
            st.session_state["pca"] = pca
            st.success("Customer segments created.")
        except Exception as e:
            show_exception(e)
    if "profile" in st.session_state:
        profile = st.session_state["profile"]
        metrics = st.columns(3)
        metrics[0].metric("Customers segmented", f"{len(st.session_state['rfm']):,}")
        metrics[1].metric("Groups created", str(profile.segment_id.nunique()))
        metrics[2].metric("PCA variance", f"{sum(st.session_state['pca']):.1%}")
        st.subheader("Segment profile")
        st.dataframe(profile.round(2), use_container_width=True)
        st.subheader("K-means comparison")
        st.dataframe(st.session_state["kdiag"].round(3), use_container_width=True)
        st.subheader("Customer-level results")
        st.dataframe(st.session_state["rfm"].head(30), use_container_width=True)
        st.caption("The project saves the segment assignments to `outputs/customer_segments.csv`.")

# --------------------------- Lapse model ---------------------------
elif page == "4 · Lapse prediction":
    section_header("STEP 04", "Customer lapse prediction", "Train the existing model to estimate which customers may not purchase in the next period.")
    st.write("The model compares logistic regression and random forest pipelines using the existing training and evaluation setup.")
    if st.button("Build and evaluate lapse model", type="primary"):
        try:
            module = import_module("src.customer_models")
            result, output = capture_call(module.build_lapse_model)
            st.session_state["lapse_result"] = result
            st.session_state["lapse_output"] = output
            st.success("Lapse model run completed.")
        except Exception as e:
            show_exception(e)
    if "lapse_result" in st.session_state:
        result = st.session_state["lapse_result"]
        st.metric("Customers in model cohort", result.get("cohort_rows", "—"))
        st.metric("Customers labelled lapsed", result.get("lapsed", "—"))
        for model_name, metrics in result.get("models", {}).items():
            with st.expander(f"{model_name.title()} model results", expanded=True):
                st.json(metrics)
        st.subheader("Illustrative retention list")
        st.dataframe(result.get("retention_list", pd.DataFrame()), use_container_width=True)
        st.caption("The model file and retention list are written under `outputs/`.")

# --------------------------- Triage ---------------------------
elif page == "5 · Support ticket triage":
    section_header("STEP 05", "Support ticket triage", "Classify incoming tickets and route them to the appropriate queue.")
    st.write("The module checks empty and long messages, masks selected personal details, retries temporary failures and sends uncertain results to human review.")
    token_budget = st.number_input("Token budget", min_value=1, max_value=500000, value=100000, step=1000)
    if not status["mock_llm"]:
        st.error("Missing `mock_llm.py`. The uploaded `triage.py` imports it, so this stage cannot run until that project file is present.")
    if st.button("Run ticket triage", type="primary", disabled=not status["mock_llm"]):
        try:
            module = import_module("src.triage")
            (result, summary), run_log = capture_call(
                module.run_pipeline, prompt=module.FEW, token_budget=int(token_budget)
            )
            st.session_state["triage_result"] = result
            st.session_state["triage_summary"] = summary
            st.session_state["triage_run_log"] = run_log
            st.success("Ticket triage completed.")
        except Exception as e:
            show_exception(e)
    if "triage_result" in st.session_state:
        result = st.session_state["triage_result"]
        st.json(st.session_state["triage_summary"])
        st.dataframe(result, use_container_width=True)
        if "route" in result.columns:
            st.bar_chart(result["route"].value_counts())
        if st.session_state.get("triage_run_log"):
            with st.expander("Triage execution log"):
                st.code(st.session_state["triage_run_log"])

# --------------------------- Policy assistant ---------------------------
elif page == "6 · Policy assistant":
    section_header("STEP 06", "Company policy assistant", "Ask a question and retrieve the most relevant text from the policy documents.")
    st.write("The current module uses TF-IDF and cosine similarity to retrieve policy passages, then asks the local mock language model to answer from that context.")
    question = st.text_area("Enter a policy question", placeholder="Example: What delivery time makes a completed order eligible for a full refund?")
    if not status["mock_llm"]:
        st.error("Missing `mock_llm.py`. The policy module imports it.")
    if not status["policies"]:
        st.warning("No `.txt` policy files found in `data/policies/`.")
    if st.button("Ask policy assistant", type="primary", disabled=not (status["mock_llm"] and bool(status["policies"]) and bool(question.strip()))):
        try:
            module = import_module("src.policy_rag")
            rag = module.PolicyRAG(chunk_size=40, overlap=10)
            result = rag.answer(question.strip())
            st.subheader("Answer")
            st.write(result["answer"])
            st.caption("Sources: " + ", ".join(result["sources"]))
            with st.expander("Retrieved policy passages"):
                for hit in result["retrieved"]:
                    st.markdown(f"**{hit['source']} · similarity {hit['score']:.3f}**")
                    st.write(hit["text"])
        except Exception as e:
            show_exception(e)

# --------------------------- Refund ---------------------------
elif page == "7 · Refund workflow":
    section_header("STEP 07", "Refund-support workflow", "Walk through the project's database-backed refund agent.")
    st.warning("The uploaded refund module writes a local ledger record. It does not transfer money or connect to a payment provider.")
    order_id = st.text_input("Order ID", placeholder="Example: ORD-000001")
    request_text = st.text_area("Customer request", value="Please check whether my delayed order is eligible for a refund.")
    if not status["mock_llm"]:
        st.error("Missing `mock_llm.py`. The refund agent imports it.")
    if not status["policies"]:
        st.warning("No policy `.txt` files found in `data/policies/`. The refund module initializes the policy retriever when imported.")
    if st.button("Run refund-support agent", type="primary", disabled=not (status["mock_llm"] and bool(status["policies"]) and order_id.strip())):
        try:
            module = import_module("src.refund_agent")
            prompt = f"{request_text}\nOrder ID: {order_id.strip()}"
            result, output = capture_call(module.run_agent, prompt, scenario_id="browser-demo")
            st.session_state["refund_result"] = result
            st.success("Refund-support workflow finished.")
        except Exception as e:
            show_exception(e)
    if "refund_result" in st.session_state:
        st.subheader("Workflow result")
        st.json(st.session_state["refund_result"])
        st.caption("Review the result and ledger entry. This is a local demonstration, not a real refund.")

# --------------------------- Churn ---------------------------
elif page == "8 · Churn analysis":
    section_header("STEP 08", "Customer churn analysis", "Review descriptive churn patterns and estimate future churn risk.")
    st.write("The churn module uses `data/clean/customers.csv`, `orders.csv` and `products.csv`. Ticket data is optional for descriptive comparisons.")
    churn_days = st.slider("Inactivity threshold (days)", min_value=30, max_value=180, value=90, step=5)
    as_of = st.date_input("Analysis date (optional cutoff)", value=None)
    if st.button("Run churn analysis", type="primary"):
        try:
            module = import_module("src.churn_analysis")
            kwargs = {"churn_days": int(churn_days), "output_dir": str(ROOT / "outputs" / "churn")}
            if as_of is not None:
                kwargs["as_of_date"] = str(as_of)
            (customer_analysis, summary), output = capture_call(module.run_churn_analysis, **kwargs)
            st.session_state["churn_customers"] = customer_analysis
            st.session_state["churn_summary"] = summary
            st.session_state["churn_output"] = output
            st.success("Churn analysis completed.")
        except Exception as e:
            show_exception(e)

    if "churn_summary" in st.session_state:
        summary = st.session_state["churn_summary"]
        values = dict(zip(summary["metric"], summary["value"]))
        m1, m2, m3 = st.columns(3)
        m1.metric("Total customers", values.get("Total customers", "—"))
        m2.metric("Churned customers", values.get("Churned customers", "—"))
        m3.metric("Churn rate", f"{values.get('Churn rate (%)', '—')}%")

        st.subheader("Churn summary")
        st.dataframe(summary, use_container_width=True)

        st.subheader("Churn visualisations")
        chart_dir = ROOT / "outputs" / "churn" / "charts"
        chart_titles = {
            "01_churn_distribution.png": "Customer churn distribution",
            "02_churn_by_city.png": "Churn rate by city",
            "03_churn_by_age_group.png": "Churn rate by age group",
            "04_revenue_by_product_category.png": "Revenue by product category",
            "05_model_confusion_matrix.png": "Predictive model — confusion matrix",
            "06_top_churn_predictors.png": "Top 15 churn predictors",
        }
        chart_files = [
            (filename, title)
            for filename, title in chart_titles.items()
            if (chart_dir / filename).is_file()
        ]
        if chart_files:
            for offset in range(0, len(chart_files), 2):
                cols = st.columns(2)
                for col, (filename, title) in zip(cols, chart_files[offset:offset + 2]):
                    with col:
                        st.markdown(f"**{title}**")
                        st.image(str(chart_dir / filename), use_container_width=True)
            st.caption("Charts are also saved as PNG files in `outputs/churn/charts/`.")
        else:
            st.info("No churn charts were found. Run the churn analysis again to generate them.")

        st.subheader("Customer-level churn results")
        st.dataframe(st.session_state["churn_customers"].head(100), use_container_width=True)
        st.caption("Detailed CSV reports are saved in `outputs/churn/`.")
        with st.expander("Run log"):
            st.code(st.session_state.get("churn_output", ""))

# --------------------------- Outputs ---------------------------
elif page == "Project outputs":
    section_header("PROJECT FILES", "Generated outputs", "Browse the reports and database created by the project stages.")
    output_dir = ROOT / "outputs"
    if not output_dir.exists():
        st.info("No outputs folder yet. Run the project stages first.")
    else:
        files = sorted(p for p in output_dir.rglob("*") if p.is_file())
        if not files:
            st.info("The outputs folder is currently empty.")
        else:
            st.write(f"Found **{len(files)}** output files.")
            for path in files:
                rel = path.relative_to(ROOT)
                with st.expander(str(rel)):
                    if path.suffix.lower() == ".csv":
                        try:
                            df = pd.read_csv(path)
                            st.dataframe(df.head(100), use_container_width=True)
                            st.download_button(
                                "Download CSV",
                                data=path.read_bytes(),
                                file_name=path.name,
                                mime="text/csv",
                                key=f"download_{str(rel)}",
                            )
                        except Exception:
                            st.download_button("Download file", path.read_bytes(), file_name=path.name)
                    else:
                        st.caption(f"{path.stat().st_size:,} bytes")
                        st.download_button(
                            "Download file", path.read_bytes(),
                            file_name=path.name, key=f"download_{str(rel)}"
                        )
    db_path = ROOT / "data" / "instamart.db"
    if db_path.exists():
        st.subheader("SQLite database tables")
        try:
            with sqlite3.connect(db_path) as con:
                tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", con)
            st.dataframe(tables, use_container_width=True)
        except Exception as e:
            st.error(str(e))

st.sidebar.divider()
st.sidebar.caption("For local/private demonstration, run this app on your own computer. To access it from outside your network, deploy it to a hosting service with appropriate data protection.")
