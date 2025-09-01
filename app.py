import streamlit as st
import pandas as pd
import base64
from pathlib import Path

# ------------------ background helpers ------------------
def image_to_base64_uri(img_path: Path) -> str | None:
    try:
        data = img_path.read_bytes()
        mime = "image/jpeg" if img_path.suffix.lower() in [".jpg", ".jpeg"] else "image/png"
        return f"data:{mime};base64," + base64.b64encode(data).decode("utf-8")
    except Exception:
        return None

def inject_bg():
    # try assets/hero.jpg, then hero.jpg
    for p in [Path("assets/hero.jpg"), Path("hero.jpg")]:
        if p.exists():
            uri = image_to_base64_uri(p)
            break
    else:
        uri = None

    css_bg = f"""
    .stApp {{
      background-image: url("{uri}");
      background-size: cover;
      background-position: center;
      background-repeat: no-repeat;
      background-attachment: fixed;
    }}
    """ if uri else ""

    st.markdown(f"""
    <style>
      {css_bg}

      /* dark overlay for readability */
      .stApp::before {{
        content:"";
        position: fixed; inset: 0;
        background: rgba(0,0,0,.65);
        z-index: -1;
      }}

      /* ONE solid black container */
      .black-container {{
        max-width: 980px;
        margin: 48px auto;
        background: rgba(0,0,0,0.9);
        border: 1px solid rgba(255,255,255,.2);
        border-radius: 22px;
        box-shadow: 0 20px 50px rgba(0,0,0,.5);
        padding: 36px 36px 28px 36px;
      }}

      .card-title {{
        margin: 0 0 28px 0;
        text-align: center;
        font-size: 52px;
        font-weight: 900;
        color: #fff;
        letter-spacing: .3px;
        text-shadow: 0 4px 16px rgba(0,0,0,.45);
      }}

      /* inputs inside the black box */
      .stSelectbox > div > div {{
        background: #111;
        border: 1px solid rgba(255,255,255,.2);
        border-radius: 14px;
      }}
      .stSelectbox div[data-baseweb="select"] > div {{
        min-height: 56px;
        padding: 8px 12px;
        color: #f8fafc !important;
        background: #111 !important;
      }}

      .stSlider > div {{
        background: #111;
        border: 1px solid rgba(255,255,255,.2);
        border-radius: 14px;
        padding: 14px;
      }}

      .black-container label {{
        color: #f1f5f9 !important;
        font-weight: 700 !important;
      }}

      .stTable thead th {{
        background: #000 !important;
        color: #fff !important;
        text-align: center !important;
      }}
      .stTable tbody td {{
        background: #111 !important;
        color: #fff !important;
        text-align: center !important;
      }}
    </style>
    """, unsafe_allow_html=True)


# ------------------ app ------------------
st.set_page_config(page_title="Top 5 Restaurants", page_icon="🍽️", layout="centered")
inject_bg()

# demo data
restaurants = pd.DataFrame({
    "Restaurant": ["Ishaara", "Darshan", "Tettoricca", "Poise", "PizzaExpress"],
    "Price": [1400, 950, 1200, 1200, 1400],
    "Dishes Served": [
        "biryani, north indian, kebab, mughlai",
        "continental, north indian, chinese, mexican, fast food, desserts, juices",
        "north indian",
        "asian",
        "pizza, italian, salad, bakery, beverages, coffee, pasta"
    ]
})

all_cuisines = sorted({c.strip().lower() for dishes in restaurants["Dishes Served"] for c in dishes.split(",")})

# ---- Big black box ----
st.markdown("<div class='black-container'>", unsafe_allow_html=True)
st.markdown("<div class='card-title'>Top 5 Restaurants</div>", unsafe_allow_html=True)

cuisine = st.selectbox("Select Cuisine", ["Any"] + all_cuisines, index=0)
pmin, pmax = int(restaurants["Price"].min()), int(restaurants["Price"].max())
price_range = st.slider("Select Price Range", min_value=pmin, max_value=pmax, value=(pmin, pmax), step=50)

df = restaurants.copy()
if cuisine != "Any":
    df = df[df["Dishes Served"].str.contains(fr"\b{cuisine}\b", case=False, na=False)]
df = df[(df["Price"] >= price_range[0]) & (df["Price"] <= price_range[1])]

st.table(df if not df.empty else pd.DataFrame([{"Restaurant": "No results"}]))
st.markdown("</div>", unsafe_allow_html=True)
