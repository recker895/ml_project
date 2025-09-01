# app.py
# -------------------------------------------------
# pip install streamlit pandas numpy
# streamlit run app.py

import ast, re
import numpy as np
import pandas as pd
import streamlit as st
from pathlib import Path

# ---------- paths ----------
ROOT = Path(__file__).parent
CSV_PATH = ROOT / "restaurant_with_clean_dishes.csv"
ASSETS = ROOT / "assets"
CSS_FILE = ASSETS / "style.css"      # your screenshot shows "style.css"
HERO_IMG = ASSETS / "hero.jpg"

# ---------- inject CSS ----------
def inject_css(path: Path):
    if path.exists():
        st.markdown(f"<style>{path.read_text()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"{path.as_posix()} not found – using Streamlit defaults.")

inject_css(CSS_FILE)

# ---------- helpers ----------
def safe_list(x):
    if isinstance(x, list): return x
    if isinstance(x, str):
        x = x.strip()
        if x.startswith("[") and x.endswith("]"):
            try:
                v = ast.literal_eval(x)
                return v if isinstance(v, list) else [x]
            except:
                return [x]
        return [x] if x else []
    return []

def extract_price_from_text(val):
    if pd.isna(val): return np.nan
    s = str(val)
    m = re.search(r"([\d,]+)\s*for\s*two", s, flags=re.IGNORECASE)
    if m:
        return float(m.group(1).replace(",", ""))
    nums = re.findall(r"\d[\d,]*", s)
    return float(nums[0].replace(",", "")) if nums else np.nan

# ---------- page ----------
st.set_page_config(page_title="Top 5 Restaurants", page_icon="🍽️", layout="centered")

# Title (use CSS for background/overlay in style.css)
st.markdown("<h1>Top 5 Restaurants</h1>", unsafe_allow_html=True)

# ---------- data load ----------
try:
    df = pd.read_csv(CSV_PATH)
except Exception as e:
    st.error(f"Could not load CSV at `{CSV_PATH.name}`.\n{e}")
    st.stop()

# Ensure numeric Price
if "Price" not in df.columns:
    if "Price for Two" in df.columns:
        df["Price"] = df["Price for Two"].apply(extract_price_from_text).astype(float)
    else:
        df["Price"] = np.nan

# Ensure dishes tokens
if "Dishes_tokens" not in df.columns:
    # derive from "Dishes" if needed
    sep = re.compile(r"[,\|/•&]+")
    def split_clean(s):
        if pd.isna(s): return []
        parts = sep.split(str(s))
        toks = []
        for p in parts:
            t = re.sub(r"\s+", " ", p.strip().lower())
            if not t: continue
            if "for two" in t or any(ch.isdigit() for ch in t) or "₹" in t or "$" in t or "rs" in t:
                continue
            toks.append(t)
        return toks
    df["Dishes_tokens"] = df["Dishes"].apply(split_clean) if "Dishes" in df.columns else [[] for _ in range(len(df))]

df["Dishes_tokens"] = df["Dishes_tokens"].apply(safe_list)

# Prefer provided cuisines; else derive a lightweight set
if "Cuisines_tokens" in df.columns:
    df["Cuisines_tokens"] = df["Cuisines_tokens"].apply(safe_list)
    df["Cuisine_tokens_effective"] = df["Cuisines_tokens"]
else:
    CUISINE_KEYWORDS = {
        "north indian","south indian","maharashtrian","mughlai","chinese",
        "continental","italian","asian","seafood","oriental","fast food",
        "bar food","desserts","beverages","cafe","coffee"
    }
    df["Cuisine_tokens_effective"] = df["Dishes_tokens"].apply(
        lambda xs: [t for t in xs if t in CUISINE_KEYWORDS]
    )

# ---------- UI (simple like your mock) ----------
# Dropdowns sit right under the title; CSS handles visuals (rounded card / background)
all_cuisines = sorted({c for row in df["Cuisine_tokens_effective"] for c in row})
cuisine_choice = st.selectbox("Cuisine", ["What do you want to eat?"] + all_cuisines, index=0, key="cuisine_select")

if df["Price"].notna().any():
    price_values = sorted(set(int(p) for p in df["Price"].dropna().unique()))
    price_choice = st.selectbox("Price", ["$"] + price_values, index=0, key="price_select")
else:
    price_choice = st.selectbox("Price", ["$"], index=0, key="price_select")

# ---------- filter ----------
df_f = df.copy()
if cuisine_choice != "What do you want to eat?":
    df_f = df_f[df_f["Cuisine_tokens_effective"].apply(lambda toks: cuisine_choice in (toks or []))]
if price_choice != "$":
    df_f = df_f[df_f["Price"] == int(price_choice)]

# ---------- rank ----------
if "rec_score" in df_f.columns:
    sort_cols = ["rec_score", "Rating"] + (["review_count"] if "review_count" in df_f.columns else [])
    df_f = df_f.sort_values(by=sort_cols, ascending=[False]*len(sort_cols))
elif "Rating" in df_f.columns:
    df_f = df_f.sort_values(by="Rating", ascending=False)

top5 = df_f.head(5).copy()

# ---------- output ----------
def fmt_dishes(x): return ", ".join(safe_list(x))

if top5.empty:
    st.info("No restaurants match the selected filters.")
else:
    out = top5[["restaurant", "Price", "Dishes_tokens"]].copy()
    out.rename(columns={"restaurant":"Restaurant", "Dishes_tokens":"Dishes Served"}, inplace=True)
    out["Dishes Served"] = out["Dishes Served"].apply(fmt_dishes)
    out.index = range(1, len(out) + 1)  # 1..5 numbering
    st.table(out)
