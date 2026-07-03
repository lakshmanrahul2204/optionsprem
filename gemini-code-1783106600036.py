# filename: app.py
import streamlit as st
import pandas as pd
import numpy as np
from growwapi import GrowwAPI
import traceback
from datetime import date, timedelta

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OptionsSense | Fair Value Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght=400;600&family=Syne:wght=400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

/* ── Hide Streamlit's white top toolbar/header ───────────────────────────── */
[data-testid="stHeader"] {
    display: none !important;
}

/* Remove the gap Streamlit reserves for the hidden header */
.stApp > header { display: none !important; }
.block-container {
    padding-top: 1.5rem !important;
}

.stApp {
    background: #0a0e1a;
    color: #e8eaf6;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0d1224 !important;
    border-right: 1px solid #1e2a4a;
}

/* Sidebar collapse/expand arrow — force white */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] *,
[data-testid="collapsedControl"],
[data-testid="collapsedControl"] * {
    color: #ffffff !important;
    fill: #ffffff !important;
    stroke: #ffffff !important;
}

/* ── Top brand bar ───────────────────────────────────────────────────────── */
.brand-bar {
    background: linear-gradient(135deg, #1a237e 0%, #0d1224 100%);
    border: 1px solid #283593;
    border-radius: 12px;
    padding: 1.2rem 1.8rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.brand-title {
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, #7986cb, #64b5f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}
.brand-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #90a4ae;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ── Streamlit native widget labels ──────────────────────────────────────── */
label,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] {
    color: #c5cae9 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: #c5cae9 !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] h3 {
    color: #e8eaf6 !important;
}

/* ── Metric cards ────────────────────────────────────────────────────────── */
.metric-card {
    background: #111827;
    border: 1px solid #1e2a4a;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #90a4ae;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.3rem;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.4rem;
    font-weight: 600;
    color: #7986cb;
}
.metric-value.positive { color: #66bb6a; }
.metric-value.negative { color: #ef5350; }

/* ── Fair value result box ───────────────────────────────────────────────── */
.result-box {
    background: linear-gradient(135deg, #1a237e22, #0d47a122);
    border: 2px solid #3949ab;
    border-radius: 14px;
    padding: 2rem;
    text-align: center;
    margin-top: 1rem;
}
.result-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #7986cb;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.result-value {
    font-size: 3rem;
    font-weight: 800;
    color: #e8eaf6;
    line-height: 1;
}
.result-diff {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    margin-top: 0.5rem;
}

/* ── Taylor terms ────────────────────────────────────────────────────────── */
.taylor-box {
    background: #0d1224;
    border: 1px solid #1e2a4a;
    border-radius: 10px;
    padding: 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
}
.taylor-row {
    display: flex;
    justify-content: space-between;
    padding: 0.3rem 0;
    border-bottom: 1px solid #1e2a4a11;
    color: #90a4ae;
}
.taylor-row .term { color: #7986cb; }
.taylor-row .contrib { font-weight: 600; }
.taylor-total {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0 0;
    border-top: 1px solid #3949ab;
    color: #e8eaf6;
    font-weight: 600;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #3949ab, #1a237e) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.85 !important;
    transform: translateY(-1px) !important;
}

/* ── Inputs ──────────────────────────────────────────────────────────────── */
.stTextInput input, .stNumberInput input, .stSelectbox select {
    background: #111827 !important;
    border: 1px solid #1e2a4a !important;
    color: #e8eaf6 !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Info / warning boxes ────────────────────────────────────────────────── */
.stAlert {
    border-radius: 10px !important;
}

/* ── Mobile: hide sidebar entirely, we use inline login card ────────────── */
@media (max-width: 768px) {
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
}

/* ── Login card (inline, shown on all screen sizes) ──────────────────────── */
.login-card {
    background: #0d1224;
    border: 1px solid #1e2a4a;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.2rem;
}
.login-card-connected {
    background: #0a1a0f;
    border: 1px solid #1b5e20;
    border-radius: 12px;
    padding: 0.8rem 1.5rem;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.connected-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #66bb6a;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.section-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #90a4ae;
    letter-spacing: 2px;
    text-transform: uppercase;
    border-bottom: 1px solid #1e2a4a;
    padding-bottom: 0.4rem;
    margin: 1.2rem 0 0.8rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Session State Init ───────────────────────────────────────────────────────
for key in ["groww", "greeks_data", "spot_ltp", "option_ltp", "trading_symbol", "underlying"]:
    if key not in st.session_state:
        st.session_state[key] = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ─── Taylor Series Fair Value ────────────────────────────────────────────────
def compute_fair_value(current_premium, delta, gamma, theta, vega,
                        current_spot, target_spot, days_forward=0, iv_change=0.0):
    """
    Taylor Series expansion of option price around current spot:
    P(S*) ≈ P(S) + Δ·ΔS + ½·Γ·ΔS² + θ·Δt + ν·Δσ
    """
    dS   = target_spot - current_spot
    dt   = days_forward / 365.0
    d_iv = iv_change / 100.0

    delta_term = delta * dS
    gamma_term = 0.5 * gamma * dS ** 2
    theta_term = theta * days_forward
    vega_term  = vega * d_iv

    fair = current_premium + delta_term + gamma_term + theta_term + vega_term

    breakdown = {
        "Δ · ΔS  (Delta)":     delta_term,
        "½Γ · ΔS²  (Gamma)":   gamma_term,
        "θ · Δt  (Theta)":     theta_term,
        "ν · Δσ  (Vega)":      vega_term,
    }
    return max(fair, 0.0), breakdown

# ─── Brand Bar ───────────────────────────────────────────────────────────────
st.markdown("""
<div class='brand-bar'>
    <div>
        <div class='brand-title'>OptionsSense</div>
        <div class='brand-sub'>Fair Value Calculator · Taylor Series · Groww API</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Inline Login / Status Card ──────────────────────────────────────────────
if not st.session_state.authenticated:
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("#### 🔐 Connect to Groww")
    st.caption("Enter your Groww API Auth Token.")

    auth_token_input = st.text_input("API Auth Token", type="password",
                                 placeholder="Your Groww API Auth Token",
                                 help="Access token generated using your API Key and Secret")

    if st.button("Connect to Groww →", use_container_width=True):
        if not auth_token_input:
            st.error("Please enter your API Auth Token.")
        else:
            with st.spinner("Authenticating…"):
                try:
                    # Initializing directly using the token provided per documentation
                    st.session_state.groww         = GrowwAPI(auth_token_input)
                    st.session_state.authenticated = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Authentication failed: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("ℹ️ How it works"):
        st.markdown("""
**Step 1 – Authenticate**
- Place your generated **API Auth Token** inside the interface above.
- Click *Connect to Groww*

**Step 2 – Fetch Greeks**
- Select underlying, expiry, strike, and option type
- Click *Fetch Greeks & LTP*

**Step 3 – Calculate Fair Value**""")
