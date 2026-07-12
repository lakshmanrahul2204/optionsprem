import streamlit as st
import pandas as pd
import numpy as np
import traceback
from datetime import date, timedelta
from growwapi import GrowwAPI

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OptionsPrem | Fair Value Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }

/* Hide Streamlit white top toolbar */
[data-testid="stHeader"] { display: none !important; }
.stApp > header { display: none !important; }
.block-container { padding-top: 1.5rem !important; }

.stApp { background: #0a0e1a; color: #e8eaf6; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d1224 !important;
    border-right: 1px solid #1e2a4a;
}

/* Sidebar collapse arrow — force white */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] *,
[data-testid="collapsedControl"],
[data-testid="collapsedControl"] * {
    color: #ffffff !important;
    fill: #ffffff !important;
    stroke: #ffffff !important;
}

/* Mobile: hide sidebar, use inline login card */
@media (max-width: 768px) {
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] { display: none !important; }
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
}

/* Brand bar */
.brand-bar {
    background: linear-gradient(135deg, #1a237e 0%, #0d1224 100%);
    border: 1px solid #283593; border-radius: 12px;
    padding: 1.2rem 1.8rem; margin-bottom: 1.5rem;
}
.brand-title {
    font-size: 1.8rem; font-weight: 800;
    background: linear-gradient(90deg, #7986cb, #64b5f6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}
.brand-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; color: #90a4ae;
    letter-spacing: 2px; text-transform: uppercase;
}

/* Login card */
.login-card {
    background: #0d1224; border: 1px solid #1e2a4a;
    border-radius: 12px; padding: 1.2rem 1.5rem; margin-bottom: 1.2rem;
}
.login-card-connected {
    background: #0a1a0f; border: 1px solid #1b5e20;
    border-radius: 12px; padding: 0.8rem 1.5rem; margin-bottom: 1.2rem;
}
.connected-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem; color: #66bb6a;
}

/* Widget labels */
label,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] {
    color: #c5cae9 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.9rem !important; font-weight: 600 !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: #c5cae9 !important; }
[data-testid="stSidebar"] h3 { color: #e8eaf6 !important; }

/* Metric cards */
.metric-card {
    background: #111827; border: 1px solid #1e2a4a;
    border-radius: 10px; padding: 1rem 1.2rem; text-align: center;
}
.metric-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;
    color: #90a4ae; text-transform: uppercase;
    letter-spacing: 1.5px; margin-bottom: 0.3rem;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.4rem; font-weight: 600; color: #7986cb;
}
.metric-value.positive { color: #66bb6a; }
.metric-value.negative { color: #ef5350; }

/* Result box */
.result-box {
    background: linear-gradient(135deg, #1a237e22, #0d47a122);
    border: 2px solid #3949ab; border-radius: 14px;
    padding: 2rem; text-align: center; margin-top: 1rem;
}
.result-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
    color: #7986cb; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0.5rem;
}
.result-value { font-size: 3rem; font-weight: 800; color: #e8eaf6; line-height: 1; }
.result-diff  { font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; margin-top: 0.5rem; }

/* Taylor box */
.taylor-box {
    background: #0d1224; border: 1px solid #1e2a4a;
    border-radius: 10px; padding: 1.2rem;
    font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;
}
.taylor-row {
    display: flex; justify-content: space-between;
    padding: 0.3rem 0; border-bottom: 1px solid #1e2a4a22; color: #90a4ae;
}
.taylor-row .term   { color: #7986cb; }
.taylor-row .contrib { font-weight: 600; }
.taylor-total {
    display: flex; justify-content: space-between;
    padding: 0.5rem 0 0; border-top: 1px solid #3949ab;
    color: #e8eaf6; font-weight: 600;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #3949ab, #1a237e) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    letter-spacing: 0.5px !important; padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; transform: translateY(-1px) !important; }

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox select {
    background: #111827 !important; border: 1px solid #1e2a4a !important;
    color: #e8eaf6 !important; border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stAlert { border-radius: 10px !important; }

/* Section headers */
.section-header {
    font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;
    color: #90a4ae; letter-spacing: 2px; text-transform: uppercase;
    border-bottom: 1px solid #1e2a4a; padding-bottom: 0.4rem; margin: 1.2rem 0 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"]

def get_exchange(underlying: str):
    """Return the SDK exchange constant for a given underlying."""
    return "BSE" if underlying in ("SENSEX", "BANKEX") else "NSE"

# Groww trading symbol formats (confirmed from live instruments):
#
# SENSEX / BANKEX (BSE):
#   {UNDERLYING}{YY}{STRIKE}{TYPE}
#   e.g. SENSEX2677800CE
#
# NIFTY only, Jan–Sep (single digit month, no leading zero):
#   {UNDERLYING}{YY}{M}{DD}{STRIKE}{TYPE}
#   e.g. NIFTY2671424500CE  (Jul 14, strike 24500)
#
# NIFTY only, Oct–Dec (single letter O/N/D):
#   {UNDERLYING}{YY}{X}{DD}{STRIKE}{TYPE}
#   e.g. NIFTY26O1325100CE, NIFTY26N1725100CE, NIFTY26D1525100CE
#
# BANKNIFTY / FINNIFTY / MIDCPNIFTY (3-letter month, all months):
#   {UNDERLYING}{YY}{MMM}{DD}{STRIKE}{TYPE}
#   e.g. BANKNIFTY25SEP28500CE

_OCT_DEC_LETTER = {10: "O", 11: "N", 12: "D"}
_BSE_UNDERLYINGS = ("SENSEX", "BANKEX")
_THREE_LETTER_UNDERLYINGS = ("BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")

def build_trading_symbol(underlying: str, expiry: date,
                          strike: int, opt_type: str) -> str:
    yy  = expiry.strftime("%y")          # "26"
    dd  = expiry.strftime("%d")          # "09" (zero-padded day)
    mmm = expiry.strftime("%b").upper()  # "SEP", "JUL" etc.

    # BSE indices — add month and day
    if underlying in _BSE_UNDERLYINGS:
        m = str(expiry.month)
        return f"{underlying}{yy}{m}{dd}{int(strike)}{opt_type}"

    # BANKNIFTY, FINNIFTY, MIDCPNIFTY — always 3-letter month
    if underlying in _THREE_LETTER_UNDERLYINGS:
        return f"{underlying}{yy}{mmm}{int(strike)}{opt_type}"

    # NIFTY — Oct/Nov/Dec use single letter
    if expiry.month >= 10:
        m = _OCT_DEC_LETTER[expiry.month]
        return f"{underlying}{yy}{m}{dd}{int(strike)}{opt_type}"

    # NIFTY — Jan–Sep use single digit month
    m = str(expiry.month)
    return f"{underlying}{yy}{m}{dd}{int(strike)}{opt_type}"

# ─── Session State ────────────────────────────────────────────────────────────
for key in ["groww", "api_key",
            "greeks_data", "spot_ltp", "option_ltp", "underlying"]:
    if key not in st.session_state:
        st.session_state[key] = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ─── Taylor Series ────────────────────────────────────────────────────────────
def compute_fair_value(current_premium, delta, gamma, theta, vega,
                       current_spot, target_spot, days_forward=0, iv_change=0.0):
    """P(S*) ≈ P(S) + Δ·ΔS + ½·Γ·ΔS² + θ·Δt + ν·Δσ"""
    dS         = target_spot - current_spot
    d_iv       = iv_change / 100.0
    delta_term = delta * dS
    gamma_term = 0.5 * gamma * dS ** 2
    theta_term = theta * days_forward   # theta is per-day from Groww API
    vega_term  = vega * d_iv
    fair       = current_premium + delta_term + gamma_term + theta_term + vega_term
    breakdown  = {
        "Δ · ΔS  (Delta)":   delta_term,
        "½Γ · ΔS²  (Gamma)": gamma_term,
        "θ · Δt  (Theta)":   theta_term,
        "ν · Δσ  (Vega)":    vega_term,
    }
    return max(fair, 0.0), breakdown

# ─── Brand Bar ────────────────────────────────────────────────────────────────
st.markdown("""
<div class='brand-bar'>
    <div>
        <div class='brand-title'>OptionsPrem</div>
        <div class='brand-sub'>Fair Value Calculator · Taylor Series · Groww API</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Inline Login ─────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("#### 🔐 Connect to Groww")
    st.caption(
        "Get your API Key & Secret from "
        "[groww.in/trade-api/api-keys](https://groww.in/trade-api/api-keys). "
        "Set up TOTP from the same page."
    )

    lc1, lc2 = st.columns(2)
    with lc1:
        api_key    = st.text_input("API Key",    type="password",
                                    placeholder="Groww API Key")
    with lc2:
        api_secret = st.text_input("API Secret", type="password",
                                    placeholder="Groww API Secret")

    if st.button("Connect to Groww →", use_container_width=True):
        if not all([api_key, api_secret]):
            st.error("Please enter both API Key and API Secret.")
        else:
            with st.spinner("Authenticating with Groww…"):
                try:
                    access_token = GrowwAPI.get_access_token(
                        api_key=api_key,
                        secret=api_secret,
                    )
                    st.session_state.groww         = GrowwAPI(access_token)
                    st.session_state.api_key       = api_key
                    st.session_state.authenticated = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Authentication failed: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("ℹ️ How to get your credentials"):
        st.markdown("""
**API Key & Secret**
1. Go to [groww.in/trade-api/api-keys](https://groww.in/trade-api/api-keys)
2. Click **Generate API Key**, give it a name, and confirm
3. Copy the **API Key** and **API Secret** shown on the same page
        """)
    st.stop()

else:
    # Connected status bar
    col_status, col_disc = st.columns([5, 1])
    with col_status:
        st.markdown(
            "<div class='login-card-connected'>"
            "<span class='connected-badge'>● Connected to Groww</span>"
            "</div>",
            unsafe_allow_html=True,
        )
    with col_disc:
        if st.button("Disconnect"):
            for key in ["groww", "api_key", "authenticated",
                        "greeks_data", "spot_ltp", "option_ltp", "underlying"]:
                st.session_state[key] = None
            st.session_state.authenticated = False
            st.rerun()

# ─── Main Layout ──────────────────────────────────────────────────────────────
col_inp, col_result = st.columns([1, 1.3], gap="large")

with col_inp:
    st.markdown("<div class='section-header'>Instrument Selection</div>",
                unsafe_allow_html=True)

    underlying = st.selectbox("Underlying", UNDERLYINGS)

    expiry_date = st.date_input(
        "Expiry Date",
        value=date.today() + timedelta(days=7),
        min_value=date.today(),
    )
# Default values based of underlying
    if underlying in _BSE_UNDERLYINGS:
        strike_price = st.number_input("Strike Price", min_value=1, step=100, value=77000)
    else:
        strike_price = st.number_input("Strike Price", min_value=1, step=50, value=24000)
# Cont..    
    option_type = st.selectbox("Option Type", ["CE", "PE"])

    # Show the resolved trading symbol so the user can verify it
    trading_symbol = build_trading_symbol(
        underlying, expiry_date, int(strike_price), option_type
    )
    st.markdown(
        f"<div style='font-family:JetBrains Mono,monospace;font-size:0.8rem;"
        f"color:#7986cb;margin-top:0.3rem;'>Symbol: {trading_symbol}</div>",
        unsafe_allow_html=True,
    )

    fetch_clicked = st.button("📡 Fetch Greeks & LTP", use_container_width=True)

    if fetch_clicked:
        with st.spinner("Fetching data from Groww…"):
            try:
                groww    = st.session_state.groww
                exchange = get_exchange(underlying)

                # ── 1. Fetch Greeks for the specific strike via get_greeks() ──
                # Uses SDK exchange constant: groww.EXCHANGE_NSE / groww.EXCHANGE_BSE
                exchange_const = (groww.EXCHANGE_BSE
                                  if underlying in ("SENSEX", "BANKEX")
                                  else groww.EXCHANGE_NSE)

                greeks_resp = groww.get_greeks(
                    exchange=exchange_const,
                    underlying=underlying,
                    trading_symbol=trading_symbol,
                    expiry=expiry_date.strftime("%Y-%m-%d"),
                )

                # ── 2. Fetch spot LTP (index) ─────────────────────────────
                spot_key = f"{exchange}_{underlying}"

                ltp_resp = groww.get_ltp(
                    segment=groww.SEGMENT_CASH,
                    exchange_trading_symbols=spot_key,
                )

                # ── 3. Parse and store ────────────────────────────────────
                # Response is nested: {"greeks": {"delta": x, "iv": x, ...}}
                g = greeks_resp.get("greeks", greeks_resp)  # drill into nested key

                def extract_ltp(resp, key):
                    """Handle get_ltp() returning either a float or a nested dict."""
                    if resp is None:
                        return 0.0
                    if isinstance(resp, (int, float)):
                        return float(resp)
                    if isinstance(resp, dict):
                        val = resp.get(key, resp)
                        if isinstance(val, (int, float)):
                            return float(val)
                        if isinstance(val, dict):
                            return float(val.get("ltp", 0) or 0)
                    return 0.0

                def extract_option_ltp(greeks):
                    """Pull option LTP from the greeks response — tries common field names."""
                    for field in ("last_price", "ltp", "close", "last_traded_price"):
                        val = greeks.get(field)
                        if val:
                            return float(val)
                    return 0.0

                st.session_state.greeks_data = {
                    "delta":              float(g.get("delta", 0) or 0),
                    "gamma":              float(g.get("gamma", 0) or 0),
                    "theta":              float(g.get("theta", 0) or 0),
                    "vega":               float(g.get("vega",  0) or 0),
                    "implied_volatility": float(g.get("iv",    0) or 0),  # field is "iv"
                }
                st.session_state.spot_ltp   = extract_ltp(ltp_resp, spot_key)
                st.session_state.option_ltp = extract_option_ltp(greeks_resp)
                st.session_state.underlying = underlying
                st.success("✅ Data fetched successfully!")

            except Exception as e:
                st.error(f"Error: {e}")
                st.code(traceback.format_exc(), language="python")

    # ── Greeks Display ────────────────────────────────────────────────────────
    if st.session_state.greeks_data:
        gd = st.session_state.greeks_data

        st.markdown("<div class='section-header'>Live Greeks</div>",
                    unsafe_allow_html=True)

        delta = gd["delta"];  gamma = gd["gamma"]
        theta = gd["theta"];  vega  = gd["vega"]
        iv    = gd["implied_volatility"]  # already in % from Groww API
        spot  = float(st.session_state.spot_ltp  or 0)
        opt_p = float(st.session_state.option_ltp or 0)

        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown(
                f"<div class='metric-card'><div class='metric-label'>Delta</div>"
                f"<div class='metric-value'>{delta:.4f}</div></div>",
                unsafe_allow_html=True)
        with g2:
            st.markdown(
                f"<div class='metric-card'><div class='metric-label'>Gamma</div>"
                f"<div class='metric-value'>{gamma:.6f}</div></div>",
                unsafe_allow_html=True)
        with g3:
            st.markdown(
                f"<div class='metric-card'><div class='metric-label'>Theta / day</div>"
                f"<div class='metric-value negative'>{theta:.4f}</div></div>",
                unsafe_allow_html=True)

        g4, g5, g6 = st.columns(3)
        with g4:
            st.markdown(
                f"<div class='metric-card'><div class='metric-label'>Vega</div>"
                f"<div class='metric-value'>{vega:.4f}</div></div>",
                unsafe_allow_html=True)
        with g5:
            st.markdown(
                f"<div class='metric-card'><div class='metric-label'>IV (%)</div>"
                f"<div class='metric-value'>{iv:.2f}%</div></div>",
                unsafe_allow_html=True)
        with g6:
            st.markdown(
                f"<div class='metric-card'><div class='metric-label'>Option LTP</div>"
                f"<div class='metric-value'>₹{opt_p:.2f}</div></div>",
                unsafe_allow_html=True)

        st.markdown(
            f"<div style='margin-top:0.8rem;font-family:JetBrains Mono,monospace;"
            f"font-size:0.8rem;color:#546e7a;'>Spot ({underlying}): "
            f"<span style='color:#e8eaf6;font-weight:600;'>₹{spot:,.2f}</span></div>",
            unsafe_allow_html=True)

# ─── Right Column: Fair Value Calculator ──────────────────────────────────────
with col_result:
    st.markdown("<div class='section-header'>Taylor Series Fair Value</div>",
                unsafe_allow_html=True)

    if not st.session_state.greeks_data:
        st.info("Fetch Greeks first using the panel on the left.")
    else:
        gd    = st.session_state.greeks_data
        delta = gd["delta"];  gamma = gd["gamma"]
        theta = gd["theta"];  vega  = gd["vega"]
        spot  = float(st.session_state.spot_ltp  or 0)
        opt_p = float(st.session_state.option_ltp or 0)

        target_spot = st.number_input(
            "🎯 Target Spot Price", value=float(spot), step=50.0,
            help="Spot price scenario you want to evaluate.",
        )

        c1, c2 = st.columns(2)
        with c1:
            days_fwd = st.number_input(
                "Days Forward (Θ decay)",
                min_value=0, max_value=90, value=0, step=1,
                help="How many calendar days ahead is your exit scenario?",
            )
        with c2:
            iv_change = st.number_input(
                "IV Change (%)",
                min_value=-50.0, max_value=50.0, value=0.0, step=0.5,
                help="Expected absolute change in IV. Leave at 0 to ignore Vega impact.",
            )

        fair_val, breakdown = compute_fair_value(
            current_premium=opt_p,
            delta=delta, gamma=gamma, theta=theta, vega=vega,
            current_spot=spot, target_spot=target_spot,
            days_forward=days_fwd, iv_change=iv_change,
        )

        diff     = fair_val - opt_p
        diff_pct = (diff / opt_p * 100) if opt_p else 0
        diff_sym = "▲" if diff >= 0 else "▼"

        st.markdown(f"""
<div class='result-box'>
    <div class='result-label'>Estimated Fair Premium</div>
    <div class='result-value'>₹{fair_val:,.2f}</div>
    <div class='result-diff' style='color:{"#66bb6a" if diff>=0 else "#ef5350"}'>
        {diff_sym} {abs(diff):.2f} ({abs(diff_pct):.1f}%) from current ₹{opt_p:.2f}
    </div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<div class='section-header' style='margin-top:1.4rem;'>"
                    "Taylor Series Breakdown</div>", unsafe_allow_html=True)

        st.markdown(f"""
<div class='taylor-box'>
    <div class='taylor-row'>
        <span>Current Premium P(S)</span>
        <span class='contrib'>₹{opt_p:.4f}</span>
    </div>""", unsafe_allow_html=True)

        for term_name, val in breakdown.items():
            color = "#66bb6a" if val >= 0 else "#ef5350"
            st.markdown(
                f"<div class='taylor-row'>"
                f"<span class='term'>{term_name}</span>"
                f"<span class='contrib' style='color:{color};'>"
                f"{'+'if val>=0 else ''}₹{val:.4f}</span></div>",
                unsafe_allow_html=True)

        st.markdown(
            f"<div class='taylor-total'>"
            f"<span>Fair Value P(S*)</span>"
            f"<span>₹{fair_val:.4f}</span>"
            f"</div></div>",
            unsafe_allow_html=True)

        # Signal
        st.markdown("<div class='section-header'>Signal</div>", unsafe_allow_html=True)

        dS = target_spot - spot
        if abs(dS) < 1:
            signal_text  = "Spot unchanged. Only Theta & Vega effects dominate."
            signal_icon  = "⏸"; signal_color = "#ffa726"
        elif fair_val > opt_p * 1.05:
            signal_text  = (f"At ₹{target_spot:,.0f} spot, the option may be worth "
                            f"~{diff_pct:.1f}% more. Bullish scenario for this leg.")
            signal_icon  = "🚀"; signal_color = "#66bb6a"
        elif fair_val < opt_p * 0.95:
            signal_text  = (f"At ₹{target_spot:,.0f} spot, the option loses "
                            f"~{abs(diff_pct):.1f}%. Adverse move for this position.")
            signal_icon  = "⚠️"; signal_color = "#ef5350"
        else:
            signal_text  = "Marginal change. Premium relatively stable at this target."
            signal_icon  = "↔️"; signal_color = "#90a4ae"

        st.markdown(
            f"<div style='background:#0d1224;border:1px solid #1e2a4a;"
            f"border-left:3px solid {signal_color};border-radius:8px;"
            f"padding:0.9rem 1.2rem;font-size:0.9rem;'>"
            f"{signal_icon} {signal_text}</div>",
            unsafe_allow_html=True)

        with st.expander("📐 Formula & Assumptions"):
            st.markdown(r"""
**Taylor Series Expansion (2nd order):**
$$P(S^*) \approx P(S) + \Delta \cdot \Delta S + \frac{1}{2} \Gamma \cdot (\Delta S)^2 + \Theta \cdot \Delta t + \nu \cdot \Delta\sigma$$

| Symbol | Greek | Meaning |
|--------|-------|---------|
| Δ | Delta | Rate of change w.r.t. spot |
| Γ | Gamma | Convexity / 2nd-order spot sensitivity |
| Θ | Theta | Time decay (per calendar day) |
| ν | Vega  | Sensitivity to IV change |

**Assumptions:**
- Greeks are local approximations — accuracy reduces for large spot moves
- Theta uses calendar days (not trading days)
- IV change is a user scenario input, not forecasted
- For very large moves, higher-order terms (Vanna, Volga) improve accuracy
            """)

        st.markdown(
            "<div style='font-size:0.7rem;color:#37474f;margin-top:1rem;'>"
            "Options involve risk. This tool is for educational purposes only. "
            "Not financial advice.</div>",
            unsafe_allow_html=True)
