import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------- PAGE CONFIGURATION ----------
st.set_page_config(layout='wide', page_title='StartUp Funding Analysis')

# ---------- LOAD DATA ----------
df = pd.read_csv("startup_cleaned.csv")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year


# =====================================================================
# ------------------------ OVERALL ANALYSIS ----------------------------
# =====================================================================
def load_overall_analysis():
    st.title('📊 Overall Startup Funding Analysis')

    # --- Compute key statistics ---
    total = round(df['amount'].sum())
    max_funding = df.groupby('startup')['amount'].max().sort_values(ascending=False).head(1).values[0]
    avg_funding = df.groupby('startup')['amount'].sum().mean()
    num_startups = df['startup'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Total Funding', f"{total} Cr")
    col2.metric('Max Funding', f"{max_funding} Cr")
    col3.metric('Average Funding', f"{round(avg_funding)} Cr")
    col4.metric('Funded Startups', num_startups)

    # --- Month-on-Month Funding Graph ---
    st.header('📈 Month-on-Month Funding Trend')
    selected_option = st.selectbox('Select Type', ['Total', 'Count'])

    if selected_option == 'Total':
        temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
    else:
        temp_df = df.groupby(['year', 'month'])['amount'].count().reset_index()

    temp_df['x_axis'] = temp_df['month'].astype(str) + '-' + temp_df['year'].astype(str)
    fig = px.line(temp_df, x='x_axis', y='amount', markers=True,
                  title=f'Month-on-Month {selected_option} of Funding')
    fig.update_layout(
        xaxis_title="Month-Year",
        yaxis_title="Amount (Cr)",
        xaxis_tickangle=60,
        margin=dict(l=40, r=20, t=60, b=100),
        xaxis=dict(automargin=True)
    )
    st.plotly_chart(fig, use_container_width=True)

    # =================================================================
    # 1️⃣ SECTOR ANALYSIS
    # =================================================================
    st.subheader("🏭 Sector Analysis")
    colA, colB = st.columns(2)

    with colA:
        top_sector_count = df['vertical'].value_counts().head(10)
        fig1 = px.pie(values=top_sector_count.values, names=top_sector_count.index,
                      title="Top Sectors by Count", hole=0.35)
        fig1.update_traces(textposition='outside', textinfo='percent+label', pull=[0.05]*len(top_sector_count))
        fig1.update_layout(showlegend=False, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig1, use_container_width=True)

    with colB:
        top_sector_sum = df.groupby('vertical')['amount'].sum().sort_values(ascending=False).head(10)
        fig2 = px.pie(values=top_sector_sum.values, names=top_sector_sum.index,
                      title="Top Sectors by Total Funding", hole=0.35)
        fig2.update_traces(textposition='outside', textinfo='percent+label', pull=[0.05]*len(top_sector_sum))
        fig2.update_layout(showlegend=False, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    # =================================================================
    # 2️⃣ TYPE OF FUNDING
    # =================================================================
    st.subheader("💰 Funding Type Distribution")
    funding_rounds = df['round'].value_counts().head(10)
    fig3 = px.bar(x=funding_rounds.values, y=funding_rounds.index,
                  orientation='h', title="Top Funding Rounds",
                  labels={'x': 'Number of Fundings', 'y': 'Funding Type'})
    fig3.update_layout(margin=dict(l=50, r=30, t=60, b=50), xaxis=dict(automargin=True), yaxis=dict(automargin=True))
    st.plotly_chart(fig3, use_container_width=True)

    # =================================================================
    # 3️⃣ CITY-WISE FUNDING DISTRIBUTION
    # =================================================================
    st.subheader("🏙️ City-wise Funding Distribution")
    city_funding = df.groupby('city')['amount'].sum().sort_values(ascending=False).head(10)
    fig4 = px.bar(x=city_funding.values, y=city_funding.index,
                  orientation='h', title="Top 10 Cities by Total Funding",
                  labels={'x': 'Total Funding (Cr)', 'y': 'City'})
    fig4.update_layout(margin=dict(l=50, r=30, t=60, b=50))
    st.plotly_chart(fig4, use_container_width=True)

    # =================================================================
    # 4️⃣ TOP STARTUPS
    # =================================================================
    st.subheader("🚀 Top Startups (Overall and Year-wise)")
    colC, colD = st.columns(2)

    with colC:
        top_startups = df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(10)
        fig5 = px.bar(x=top_startups.values, y=top_startups.index,
                      orientation='h', title="Top 10 Startups (Overall)",
                      labels={'x': 'Total Funding (Cr)', 'y': 'Startup'})
        fig5.update_layout(margin=dict(l=50, r=30, t=60, b=50))
        st.plotly_chart(fig5, use_container_width=True)

    with colD:
        selected_year = st.selectbox("Select Year", sorted(df['year'].dropna().unique().tolist()),
                                     index=len(df['year'].dropna().unique()) - 1)
        top_startups_year = df[df['year'] == selected_year].groupby('startup')['amount'].sum().sort_values(ascending=False).head(10)
        fig6 = px.bar(x=top_startups_year.values, y=top_startups_year.index,
                      orientation='h', title=f"Top Startups in {selected_year}",
                      labels={'x': 'Total Funding (Cr)', 'y': 'Startup'})
        fig6.update_layout(margin=dict(l=50, r=30, t=60, b=50))
        st.plotly_chart(fig6, use_container_width=True)

    # =================================================================
    # 5️⃣ TOP INVESTORS
    # =================================================================
    st.subheader("👔 Top Investors by Total Investment Amount")
    investor_df = df.dropna(subset=['investors']).copy()
    investor_df['investors'] = investor_df['investors'].str.split(',')
    investor_exploded = investor_df.explode('investors')
    investor_exploded['investors'] = investor_exploded['investors'].str.strip()

    top_investors = investor_exploded.groupby('investors')['amount'].sum().sort_values(ascending=False).head(10)
    fig7 = px.bar(x=top_investors.values, y=top_investors.index,
                  orientation='h', title="Top Investors by Total Funding",
                  labels={'x': 'Total Funding (Cr)', 'y': 'Investor'})
    fig7.update_layout(margin=dict(l=50, r=30, t=60, b=50))
    st.plotly_chart(fig7, use_container_width=True)

    # =================================================================
    # 6️⃣ FUNDING HEATMAP
    # =================================================================
    st.subheader("🔥 Funding Heatmap (Year vs Month)")
    heatmap_df = df.groupby(['year', 'month'])['amount'].sum().unstack().fillna(0)
    fig8 = px.imshow(heatmap_df,
                     labels=dict(x="Month", y="Year", color="Funding (Cr)"),
                     title="Funding Heatmap (Year vs Month)",
                     aspect="auto", color_continuous_scale="YlGnBu")
    fig8.update_layout(margin=dict(l=50, r=20, t=70, b=50))
    st.plotly_chart(fig8, use_container_width=True)


# =====================================================================
# ------------------------ INVESTOR DETAILS ----------------------------
# =====================================================================
def load_investor_details(investor):
    st.title(investor)

    last5_df = df[df['investors'].str.contains(investor, na=False)].head()[
        ['date', 'startup', 'vertical', 'city', 'round', 'amount']]
    st.subheader('Most Recent Investments')
    st.dataframe(last5_df)

    col1, col2 = st.columns(2)
    with col1:
        big_series = df[df['investors'].str.contains(investor, na=False)].groupby('startup')['amount'].sum().sort_values(ascending=False).head()
        fig = px.bar(x=big_series.values, y=big_series.index, orientation='h', title="Biggest Investments")
        fig.update_layout(margin=dict(l=50, r=30, t=60, b=50))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        vertical_series = df[df['investors'].str.contains(investor, na=False)].groupby('vertical')['amount'].sum()
        fig1 = px.pie(values=vertical_series.values, names=vertical_series.index,
                      title="Sectors Invested In", hole=0.35)
        fig1.update_traces(textposition='outside', textinfo='percent+label', pull=[0.05]*len(vertical_series))
        fig1.update_layout(showlegend=False, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig1, use_container_width=True)

    # YoY Investment Trend
    year_series = df[df['investors'].str.contains(investor, na=False)].groupby('year')['amount'].sum()
    fig4 = px.line(x=year_series.index, y=year_series.values, markers=True,
                   title="YoY Investment Trend")
    st.plotly_chart(fig4, use_container_width=True)

    # Similar Investors
    st.subheader("🤝 Similar Investors")
    sectors = df[df['investors'].str.contains(investor, na=False)]['vertical'].dropna().unique()
    similar_investors_df = df[df['vertical'].isin(sectors)]
    all_investors = similar_investors_df['investors'].dropna().str.split(',').sum()
    all_investors = [i.strip() for i in all_investors if i.strip() and i.strip().lower() != investor.lower()]
    similar_investors = sorted(set(all_investors))
    st.write(", ".join(similar_investors[:15]) if similar_investors else "No similar investors found.")


# =====================================================================
# ------------------------ STARTUP DETAILS -----------------------------
# =====================================================================
def load_startup_details(startup_name):
    st.title(startup_name)
    startup_df = df[df['startup'].str.lower() == startup_name.lower()]

    if startup_df.empty:
        st.error("No data found for this startup.")
        return

    founders = startup_df['founders'].iloc[0] if 'founders' in startup_df.columns else 'N/A'
    industry = startup_df['vertical'].iloc[0] if 'vertical' in startup_df.columns else 'N/A'
    subindustry = startup_df['subvertical'].iloc[0] if 'subvertical' in startup_df.columns else 'N/A'
    location = startup_df['city'].iloc[0] if 'city' in startup_df.columns else 'N/A'

    st.subheader("📌 Basic Information")
    col1, col2, col3 = st.columns(3)
    col1.metric("Founder(s)", founders)
    col2.metric("Industry", industry)
    col3.metric("Location", location)
    st.write(f"**Sub-Industry:** {subindustry}")

    st.subheader("💰 Funding Rounds")
    funding_info = startup_df[['date', 'round', 'investors', 'amount']].sort_values(by='date', ascending=False)
    st.dataframe(funding_info)

    # Funding timeline chart
    fig = px.line(startup_df, x='date', y='amount', markers=True, title=f"{startup_name} - Funding Over Time")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🏢 Similar Companies")
    similar = df[df['vertical'] == industry]['startup'].unique().tolist()
    similar = [s for s in similar if s.lower() != startup_name.lower()]
    st.write(", ".join(similar[:10]) if similar else "No similar companies found.")


# =====================================================================
# --------------------------- SIDEBAR ----------------------------------
# =====================================================================
st.sidebar.title('Startup Funding Analysis')
option = st.sidebar.selectbox('Select One', ['Overall Analysis', 'StartUp', 'Investor'])

if option == 'Overall Analysis':
    load_overall_analysis()

elif option == 'StartUp':
    selected_startup = st.sidebar.selectbox('Select StartUp', sorted(df['startup'].dropna().unique().tolist()))
    if st.sidebar.button('Find StartUp Details'):
        load_startup_details(selected_startup)

else:
    selected_investor = st.sidebar.selectbox('Select Investor', sorted(set(df['investors'].dropna().str.split(',').sum())))
    if st.sidebar.button('Find Investor Details'):
        load_investor_details(selected_investor)
