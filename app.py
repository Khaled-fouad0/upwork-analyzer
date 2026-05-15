import streamlit as st
from analyzer import analyze_job, write_proposal

st.set_page_config(
    page_title="Upwork Job Analyzer",
    page_icon="🤙🏽",
    layout="centered"
)

DECISION_CONFIG = {
    "strong": {"color": "success", "icon": "✅", "label": "STRONG OPPORTUNITY"},
    "good":   {"color": "success", "icon": "🟢", "label": "GOOD OPPORTUNITY"},
    "weak":   {"color": "warning", "icon": "🟡", "label": "WEAK OPPORTUNITY"},
    "reject": {"color": "error",   "icon": "❌", "label": "REJECT"},
}

st.title("Upwork Job Analyzer")
st.caption("Paste a job post. Get a signal-based decision and a ready proposal.")

job_post = st.text_area(
    label="Job Post",
    placeholder="Paste the full job post here...",
    height=200
)

analyze_button = st.button("Analyze", use_container_width=True)

if analyze_button:

    if not job_post.strip():
        st.warning("Please paste a job post first.")

    else:
        with st.spinner("Extracting signals..."):
            analysis = analyze_job(job_post)

        if "error" in analysis:
            st.error(f"Analysis failed: {analysis['error']}")

        else:
            decision = analysis["decision"]
            config = DECISION_CONFIG[decision]

            # ~~~DECISION BANNER~~~#
            if config["color"] == "success":
                st.success(
                    f"{config['icon']} {config['label']} — "
                    f"Score: {analysis['score']}/100 | "
                    f"Confidence: {int(analysis['confidence'] * 100)}%"
                )
            elif config["color"] == "warning":
                st.warning(
                    f"{config['icon']} {config['label']} — "
                    f"Score: {analysis['score']}/100 | "
                    f"Confidence: {int(analysis['confidence'] * 100)}%"
                )
            elif config["color"] == "error":
                st.error(
                    f"{config['icon']} {config['label']} — "
                    f"Score: {analysis['score']}/100 | "
                    f"Confidence: {int(analysis['confidence'] * 100)}%"
                )

            # ~~~SIGNALS TABLE~~~#
            st.subheader("Extracted Signals")

            signals = analysis["signals"]
            col1, col2 = st.columns(2)
            signal_list = list(signals.items())
            mid = len(signal_list) // 2

            with col1:
                for key, value in signal_list[:mid]:
                    display = ", ".join(map(str, value)) if isinstance(value, list) else (str(value) if value is not None else "—")
                    st.metric(label=key.replace("_", " ").title(), value=display)

            with col2:
                for key, value in signal_list[mid:]:
                    display = ", ".join(map(str, value)) if isinstance(value, list) else (str(value) if value is not None else "—")
                    st.metric(label=key.replace("_", " ").title(), value=display)

            # ~~~MISSING FIELDS~~~#
            if analysis["missing_fields"]:
                st.caption(
                    f"Missing signals: {', '.join(analysis['missing_fields'])}"
                )

            # ~~~JUSTIFICATION~~~#
            st.subheader("Justification")
            st.info(analysis["justification"])

            # ~~~PROPOSAL~~~#
            if decision != "reject":
                st.subheader("Generated Proposal")

                with st.spinner("Writing proposal..."):
                    proposal = write_proposal(job_post, analysis)

                st.text_area(
                    label="Ready to send:",
                    value=proposal,
                    height=250
                )

                st.download_button(
                    label="Download Proposal",
                    data=proposal,
                    file_name="proposal.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            else:
                st.subheader("Proposal")
                st.error("Job skipped — no proposal generated.")