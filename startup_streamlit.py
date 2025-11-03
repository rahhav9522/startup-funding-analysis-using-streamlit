import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------- PAGE CONFIGURATION ----------
# Sets wide layout and page title
st.set_page_config(layout='wide', page_title='StartUp Analysis')

# ---------- LOAD DATA ----------
# Load dataset (update path if needed)
df = pd.read_csv("F:\codes\dsmp\data_set\streamlit_startup_funding\\archive\startup_cleaned.csv")

# Convert date column to datetime format
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Extract month and year for time-series analysis
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year





# =====================================================================
# ------------------------ OVERALL ANALYSIS ----------------------------
# =====================================================================
def load_overall_analysis():
    """Displays overall investment statistics and MoM trends."""
    st.title('Overall Analysis')

    # --- Compute key statistics ---
    total = round(df['amount'].sum())                                 # Total investment amount
    max_funding = df.groupby('startup')['amount'].max().sort_values(ascending=False).head(1).values[0]  # Max funding in a single startup
    avg_funding = df.groupby('startup')['amount'].sum().mean()        # Average total funding per startup
    num_startups = df['startup'].nunique()                            # Total number of unique startups funded

    # --- Display statistics in metrics layout ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('Total', str(total) + ' Cr')
    with col2:
        st.metric('Max', str(max_funding) + ' Cr')
    with col3:
        st.metric('Avg', str(round(avg_funding)) + ' Cr')
    with col4:
        st.metric('Funded Startups', num_startups)

    # --- Month-on-Month graph section ---
    st.header('Month-on-Month Graph')
    selected_option = st.selectbox('Select Type', ['Total', 'Count'])

    # Choose aggregation based on user selection
    if selected_option == 'Total':
        temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
    else:
        temp_df = df.groupby(['year', 'month'])['amount'].count().reset_index()

    # Create combined x-axis (month-year)
    temp_df['x_axis'] = temp_df['month'].astype(str) + '-' + temp_df['year'].astype(str)

    # Plot line chart
    fig3, ax3 = plt.subplots()
    ax3.plot(temp_df['x_axis'], temp_df['amount'])
    plt.xticks(rotation=90)
    st.pyplot(fig3)


# =====================================================================
# ------------------------ INVESTOR DETAILS ----------------------------
# =====================================================================
def load_investor_details(investor):
    """Displays detailed investment history for a selected investor."""
    st.title(investor)

    # --- Show 5 most recent investments by investor ---
    last5_df = df[df['investors'].str.contains(investor, na=False)].head()[
        ['date', 'startup', 'vertical', 'city', 'round', 'amount']]
    st.subheader('Most Recent Investments')
    st.dataframe(last5_df)

    # --- Split into two columns for better layout ---
    col1, col2 = st.columns(2)

    # --- Biggest investments by this investor ---
    with col1:
        big_series = df[df['investors'].str.contains(investor, na=False)].groupby('startup')['amount'].sum().sort_values(ascending=False).head()
        st.subheader('Biggest Investments')
        fig, ax = plt.subplots()
        ax.bar(big_series.index, big_series.values)
        st.pyplot(fig)

    # --- Sector-wise investment distribution ---
    with col2:
        vertical_series = df[df['investors'].str.contains(investor, na=False)].groupby('vertical')['amount'].sum()
        st.subheader('Sectors Invested In')
        fig1, ax1 = plt.subplots()
        ax1.pie(vertical_series, labels=vertical_series.index, autopct="%0.01f%%")
        st.pyplot(fig1)

    # --- Stage and City distributions (two more columns) ---
    col3, col4 = st.columns(2)

    # Funding stage distribution
    with col3:
        round_series = df[df['investors'].str.contains(investor, na=False)].groupby('round')['amount'].sum()
        st.subheader('Stage Invested In')
        fig2, ax2 = plt.subplots()
        ax2.pie(round_series, labels=round_series.index, autopct="%0.01f%%")
        st.pyplot(fig2)

    # City distribution
    with col4:
        city_series = df[df['investors'].str.contains(investor, na=False)].groupby('city')['amount'].sum()
        st.subheader('City Invested In')
        fig3, ax3 = plt.subplots()
        ax3.pie(city_series, labels=city_series.index, autopct="%0.01f%%")
        st.pyplot(fig3)

    # --- Year-on-Year investment trend line ---
    year_series = df[df['investors'].str.contains(investor, na=False)].groupby('year')['amount'].sum()
    st.subheader('YoY Investment Trend')
    fig4, ax4 = plt.subplots()
    ax4.plot(year_series.index, year_series.values)
    st.pyplot(fig4)


      # --- SIMILAR INVESTORS SECTION ---
    st.subheader("🤝 Similar Investors")

    # Step 1: Get all sectors (verticals) where this investor has invested
    sectors = df[df['investors'].str.contains(investor, na=False)]['vertical'].dropna().unique()

    # Step 2: Find all investors who also invested in these sectors
    similar_investors_df = df[df['vertical'].isin(sectors)]

    # Step 3: Extract unique investors list (split by comma and flatten)
    all_investors = similar_investors_df['investors'].dropna().str.split(',').sum()
    all_investors = [i.strip() for i in all_investors if i.strip() != '' and i.strip().lower() != investor.lower()]

    # Step 4: Remove duplicates and sort
    similar_investors = sorted(set(all_investors))

    # Step 5: Display results
    if similar_investors:
        st.write(", ".join(similar_investors[:15]))  # Show top 15 similar investors
    else:
        st.write("No similar investors found.")


# =====================================================================
# ------------------------ STARTUP DETAILS -----------------------------
# =====================================================================
def load_startup_details(startup_name):
    """Displays detailed profile and funding history for a selected startup."""
    st.title(startup_name)

    # --- Filter data for selected startup ---
    startup_df = df[df['startup'].str.lower() == startup_name.lower()]

    # Handle case if no startup found
    if startup_df.empty:
        st.error("No data found for this startup.")
        return

    # --- Extract key details (with fallback if missing) ---
    founders = startup_df['founders'].iloc[0] if 'founders' in startup_df.columns else 'N/A'
    industry = startup_df['vertical'].iloc[0] if 'vertical' in startup_df.columns else 'N/A'
    subindustry = startup_df['subvertical'].iloc[0] if 'subvertical' in startup_df.columns else 'N/A'
    location = startup_df['city'].iloc[0] if 'city' in startup_df.columns else 'N/A'

    # --- Display key information in three columns ---
    st.subheader("📌 Basic Information")
    col1, col2, col3 = st.columns(3)
    col1.metric("Founder(s)", founders)
    col2.metric("Industry", industry)
    col3.metric("Location", location)
    st.write(f"**Sub-Industry:** {subindustry}")

    # --- Funding rounds table ---
    st.subheader("💰 Funding Rounds")
    funding_info = startup_df[['date', 'round', 'investors', 'amount']].sort_values(by='date', ascending=False)
    st.dataframe(funding_info)

    # --- List of similar startups in the same industry ---
    st.subheader("🏢 Similar Companies")
    similar = df[df['vertical'] == industry]['startup'].unique().tolist()
    similar = [s for s in similar if s.lower() != startup_name.lower()]

    if similar:
        st.write(", ".join(similar[:10]))  # Display top 10 similar companies
    else:
        st.write("No similar companies found.")


# =====================================================================
# --------------------------- SIDEBAR ----------------------------------
# =====================================================================
st.sidebar.title('Startup Funding Analysis')

# Main navigation selection
option = st.sidebar.selectbox('Select One', ['Overall Analysis', 'StartUp', 'Investor'])

# --- Option 1: Overall ---
if option == 'Overall Analysis':
    load_overall_analysis()
    pass

# --- Option 2: Startup Details ---
elif option == 'StartUp':
    selected_startup = st.sidebar.selectbox('Select StartUp', sorted(df['startup'].dropna().unique().tolist()))
    btn1 = st.sidebar.button('Find StartUp Details')
    if btn1:
        load_startup_details(selected_startup)
        pass

# --- Option 3: Investor Details ---
else:
    selected_investor = st.sidebar.selectbox('Select Investor', sorted(set(df['investors'].dropna().str.split(',').sum())))
    btn2 = st.sidebar.button('Find Investor Details')
    if btn2:
        load_investor_details(selected_investor)
        pass