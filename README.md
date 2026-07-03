# OptionsSense — Options Fair Value Calculator

Lakshman Rahul has created a Streamlit app that connects to your **Groww broker account** via API, fetches live Option Greeks, and calculates the **fair premium value** using a **Taylor Series Expansion** of the Black-Scholes option pricing model.

---

## Features

- 🔐 **TOTP Authentication** — Secure, no-expiry login via Groww's TOTP flow
- 📡 **Live Greeks** — Fetches Delta, Gamma, Theta, Vega, IV directly from Groww API
- 📈 **Live Spot LTP** — Real-time underlying index price
- ⚡ **Taylor Series Fair Value** — 2nd-order approximation:
  ```
  P(S*) ≈ P(S) + Δ·ΔS + ½·Γ·ΔS² + θ·Δt + ν·Δσ
  ```
- 🎯 **Scenario Analysis** — Enter any target spot, days forward, and IV shift
- 🧮 **Full Breakdown** — See every Greek's contribution to the fair value

---

## Quickstart (Local)

```bash
git clone <your-repo>
cd options_calculator
pip install -r requirements.txt
streamlit run app.py
```

---

## Deploy to Streamlit Cloud (Free)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/<your-username>/options-sense.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click **New app** → select your repo → set `app.py` as the main file
   - Click **Deploy** — it's free!

3. **Secrets (Optional — for pre-filling credentials):**
   - In Streamlit Cloud dashboard → App → ⋮ → **Edit secrets**
   - You can add:
     ```toml
     GROWW_TOTP_TOKEN = "your_token"
     GROWW_TOTP_SECRET = "your_secret"
     ```
   - Then in `app.py`, read them via `st.secrets["GROWW_TOTP_TOKEN"]`

---

## How to Get Your Groww TOTP Credentials

1. Go to [Groww Cloud API Keys](https://groww.in/trade-api/api-keys)
2. Log in to your Groww account
3. Click the dropdown arrow next to **Generate API Key**
4. Select **Generate TOTP token**
5. Name it (e.g., "OptionsSense") and continue
6. Copy the **TOTP Token** and **TOTP Secret**

> ⚠️ The TOTP Secret is shown only once. Save it securely.

---

## Taylor Series Math

The fair value of an option at a new spot price S* is approximated by:

```
P(S*) ≈ P(S)           ← current premium
       + Δ · ΔS         ← delta contribution (linear spot move)
       + ½ · Γ · ΔS²   ← gamma contribution (convexity)
       + θ · Δt         ← theta decay (time in days)
       + ν · Δσ         ← vega contribution (IV shift in %)
```

Where:
- `ΔS = S* - S` (spot move)
- `Δt` = days forward
- `Δσ` = IV change in decimal (e.g., 2% → 0.02)

---

## Important Notes

- Groww API requires an **active Trading API Subscription**
- Greeks are **local approximations** — accuracy decreases for large moves
- This tool is for **educational and analytical purposes only**
- Not financial advice. Options involve significant risk.

---

## File Structure

```
options_calculator/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # This file
```
