import streamlit as st
import pandas as pd
import base64
from pathlib import Path

# Function to convert image to base64
def image_to_base64_uri(img_path):
    with open(img_path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

# Function to inject background image and apply custom styling
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

      /* Custom Table Style */
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

      /* Adding black background to row numbers (index column) */
      .stTable tbody td:first-child {{
        background: #000 !important;
        color: #fff !important;
      }}
    </style>
    """, unsafe_allow_html=True)

# Loading Data (CSV or DataFrame)
def load_data():
    # Sample data, replace this with your actual data
    data = {
        'Restaurant': ['Ishaara', 'Darshan', 'Tettorica', 'Poise', 'PizzaExpress'],
        'Price': [1400, 950, 1200, 1200, 1400],
        'Dishes Served': ['biryani, north indian, kebab, mughlai', 
                          'continental, north indian, chinese, mexican, fast food, desserts, juices',
                          'north indian', 
                          'asian', 
                          'pizza, italian, salad, bakery, beverages, coffee, pasta']
    }
    df = pd.DataFrame(data)
    return df

# Main function to run the Streamlit app
def main():
    st.title('Top 5 Restaurants')
    inject_bg()  # Call background styling function
    
    # Load data
    df = load_data()

    # List all possible cuisines for the dropdown
    all_cuisines = ['Any', 'north indian', 'asian', 'continental', 'pizza', 'juices', 'italian']
    
    # Cuisine and Price Filter Widgets
    cuisine = st.selectbox('Select Cuisine', all_cuisines)
    price_range = st.slider('Select Price Range', min_value=500, max_value=2000, value=(950, 1400), step=50)

    # Filter Data based on user input
    filtered_df = df[(df['Price'] >= price_range[0]) & (df['Price'] <= price_range[1])]
    if cuisine != 'Any':
        filtered_df = filtered_df[filtered_df['Dishes Served'].str.contains(cuisine, case=False)]

    # Add serial numbers to the rows (starting from 1)
    filtered_df.reset_index(drop=True, inplace=True)
    filtered_df.index += 1

    # Display filtered table
    st.dataframe(filtered_df)

# Run the app
if __name__ == "__main__":
    main()
