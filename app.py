import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Load the data
@st.cache_data
def load_data():
    total_coverage = pd.read_csv("results/total_coverage.csv", index_col=0)
    monthly_coverage = pd.read_csv("results/monthly_coverage.csv", index_col=0)
    outlet_coverage = pd.read_csv("results/outlet_coverage.csv", index_col=0)
    country_coverage = pd.read_csv("results/country_coverage.csv", index_col=0)
    bias_coverage = pd.read_csv("results/bias_coverage.csv", index_col=0)
    ownership_coverage = pd.read_csv("results/ownership_coverage.csv", index_col=0)
    coverage_volatility = pd.read_csv("results/coverage_volatility.csv", index_col=0)
    coverage_trend = pd.read_csv("results/coverage_trend.csv", index_col=0)
    coverage_intensity = pd.read_csv("results/coverage_intensity.csv", index_col=0)
    coverage_consistency = pd.read_csv("results/coverage_consistency.csv", index_col=0)
    seasonal_coverage = pd.read_csv("results/seasonal_coverage.csv", index_col=0)
    seasonal_coverage_percentage = pd.read_csv(
        "results/seasonal_coverage_percentage.csv", index_col=0
    )
    dow_coverage = pd.read_csv("results/dow_coverage.csv", index_col=0)
    dow_coverage_percentage = pd.read_csv(
        "results/dow_coverage_percentage.csv", index_col=0
    )
    outlet_gini = pd.read_csv("results/outlet_gini.csv", index_col=0)

    merged_df = pd.read_csv("results/merged_df.csv")
    merged_df["published_date"] = pd.to_datetime(merged_df["published_date"])

    return (
        total_coverage,
        monthly_coverage,
        outlet_coverage,
        country_coverage,
        bias_coverage,
        ownership_coverage,
        coverage_volatility,
        coverage_trend,
        coverage_intensity,
        coverage_consistency,
        seasonal_coverage,
        seasonal_coverage_percentage,
        dow_coverage,
        dow_coverage_percentage,
        outlet_gini,
        merged_df,
    )


# Load the data
(
    total_coverage,
    monthly_coverage,
    outlet_coverage,
    country_coverage,
    bias_coverage,
    ownership_coverage,
    coverage_volatility,
    coverage_trend,
    coverage_intensity,
    coverage_consistency,
    seasonal_coverage,
    seasonal_coverage_percentage,
    dow_coverage,
    dow_coverage_percentage,
    outlet_gini,
    merged_df,
) = load_data()

# Sidebar for filters
st.sidebar.header("Filters")

# Date range filter
date_range = st.sidebar.date_input(
    "Select date range",
    [merged_df["published_date"].min(), merged_df["published_date"].max()],
)

# Conflict filter
conflicts = list(merged_df["conflict_name"].unique())
selected_conflicts = st.sidebar.multiselect(
    "Select conflicts", conflicts, default=conflicts
)

# Country filter
countries = list(merged_df["country"].unique())
selected_countries = st.sidebar.multiselect(
    "Select countries", countries, default=countries
)

# Political bias filter
biases = list(merged_df["bias"].unique())
selected_biases = st.sidebar.multiselect(
    "Select political biases", biases, default=biases
)

# Ownership type filter
ownerships = list(merged_df["ownership"].unique())
selected_ownerships = st.sidebar.multiselect(
    "Select ownership types", ownerships, default=ownerships
)

# Outlet filter
outlets = list(merged_df["outlet_name"].unique())
selected_outlets = st.sidebar.multiselect(
    "Select specific outlets", outlets, default=outlets
)

def update_dashboard():
    # Apply filters
    filtered_df = merged_df[
        (merged_df["published_date"] >= pd.Timestamp(date_range[0]))
        & (merged_df["published_date"] <= pd.Timestamp(date_range[1]))
        & (merged_df["conflict_name"].isin(selected_conflicts))
        & (merged_df["country"].isin(selected_countries))
        & (merged_df["bias"].isin(selected_biases))
        & (merged_df["ownership"].isin(selected_ownerships))
        & (merged_df["outlet_name"].isin(selected_outlets))
    ]

    # Coverage count table
    st.header("Coverage Count")
    coverage_count = (
        filtered_df.groupby(["conflict_name", "outlet_name", "ownership", "bias"])
        .size()
        .reset_index(name="Count")
    )
    st.dataframe(coverage_count)

    # Visualizations
    st.header("Visualizations")

    filtered_monthly_coverage = monthly_coverage[selected_conflicts]
    filtered_outlet_coverage = outlet_coverage[outlet_coverage.index.isin(selected_outlets)]
    filtered_country_coverage = country_coverage[country_coverage.index.isin(selected_countries)]

    st.plotly_chart(plot_overall_coverage(filtered_df))
    st.plotly_chart(plot_monthly_coverage(filtered_monthly_coverage))
    st.plotly_chart(plot_outlet_coverage(filtered_outlet_coverage))
    st.plotly_chart(plot_country_coverage(filtered_country_coverage))

    filtered_coverage_volatility =  coverage_volatility[
        coverage_volatility.index.isin(selected_conflicts)
    ]
    filtered_coverage_trend = coverage_trend[
        (coverage_trend.index.isin(selected_conflicts))
    ]
    filtered_coverage_intensity = coverage_intensity[
        coverage_intensity.index.isin(selected_conflicts)
    ]
    filtered_coverage_consistency = coverage_consistency[
        coverage_consistency.index.isin(selected_conflicts)
    ]
    filtered_seasonal_coverage_percentage  = seasonal_coverage_percentage[selected_conflicts]
    filtered_dow_coverage_percentage = dow_coverage_percentage[selected_conflicts]
    filtered_outlet_gini = outlet_gini[
        outlet_gini.index.isin(selected_conflicts)
    ]

    # Update these functions to use filtered_df
    st.plotly_chart(plot_volatility_trend(filtered_coverage_volatility, filtered_coverage_trend))
    st.plotly_chart(plot_intensity_consistency(filtered_coverage_intensity, filtered_coverage_consistency))
    st.plotly_chart(plot_seasonal_coverage(filtered_seasonal_coverage_percentage))
    st.plotly_chart(plot_dow_coverage(filtered_dow_coverage_percentage))
    st.plotly_chart(plot_outlet_gini(filtered_outlet_gini))


# Overall conflict coverage
def plot_overall_coverage(df):
    conflict_counts = df["conflict_name"].value_counts()
    total = conflict_counts.sum()
    percentages = (conflict_counts / total) * 100

    fig = px.bar(
        x=percentages.index,
        y=percentages.values,
        title="Overall Conflict Coverage",
        labels={"x": "Conflict", "y": "Coverage Percentage"},
        color=percentages.index,
    )
    fig.update_layout(showlegend=False, xaxis_tickangle=-45)
    return fig


# Monthly conflict coverage
def plot_monthly_coverage(monthly_coverage):
    monthly_coverage_melted = monthly_coverage.reset_index().melt(
        id_vars=["month_year"], var_name="conflict", value_name="coverage"
    )
    monthly_coverage_melted["month_year"] = monthly_coverage_melted[
        "month_year"
    ].astype(str)

    fig = px.area(
        monthly_coverage_melted,
        x="month_year",
        y="coverage",
        color="conflict",
        title="Monthly Conflict Coverage",
        labels={
            "month_year": "Date",
            "coverage": "Number of Articles",
            "conflict": "Conflict",
        },
    )
    return fig


# Coverage by outlet
def plot_outlet_coverage(outlet_coverage):
    outlet_coverage_percentage = (
        outlet_coverage.div(outlet_coverage.sum(axis=1), axis=0) * 100
    )

    fig = px.imshow(
        outlet_coverage_percentage,
        title="Coverage by Outlet",
        labels=dict(x="Conflict", y="Outlet", color="Coverage Percentage"),
        aspect="auto",
        color_continuous_scale="YlOrRd",
    )
    fig.update_xaxes(side="top")
    return fig

# Coverage by country
def plot_country_coverage(country_coverage):
    country_coverage_percentage = (
        country_coverage.div(country_coverage.sum(axis=1), axis=0) * 100
    )
    country_coverage_melted = country_coverage_percentage.reset_index().melt(
        id_vars=["country"], var_name="conflict", value_name="coverage"
    )

    fig = px.bar(
        country_coverage_melted,
        x="country",
        y="coverage",
        color="conflict",
        title="Coverage by Country",
        labels={
            "country": "Country",
            "coverage": "Coverage Percentage",
            "conflict": "Conflict",
        },
        barmode="group",
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def plot_volatility_trend(coverage_volatility, coverage_trend):
    df = pd.merge(coverage_volatility, coverage_trend, left_index=True, right_index=True)
    df.columns = ['volatility', 'trend']
    df['conflict'] = df.index
    
    fig = px.scatter(df, x='volatility', y='trend', text='conflict',
                     title='Conflict Coverage Volatility vs Trend',
                     labels={'volatility': 'Volatility', 'trend': 'Trend'},
                     hover_data=['conflict'])
    fig.update_traces(textposition='top center')
    return fig


def plot_intensity_consistency(coverage_intensity, coverage_consistency):
    df = pd.merge(coverage_intensity, coverage_consistency, left_index=True, right_index=True)
    df.columns = ['intensity', 'consistency']
    df['conflict'] = df.index
    
    fig = px.scatter(df, x='intensity', y='consistency', text='conflict',
                     title='Conflict Coverage Intensity vs Consistency',
                     labels={'intensity': 'Average Articles per Day', 'consistency': 'Percentage of Days with Coverage'},
                     hover_data=['conflict'])
    fig.update_traces(textposition='top center')
    return fig

def plot_seasonal_coverage(seasonal_coverage_percentage):

    fig = px.imshow(
        seasonal_coverage_percentage,
        title="Seasonal Coverage Percentage",
        labels=dict(x="Conflict", y="Season", color="Coverage Percentage"),
        aspect="auto",
        color_continuous_scale="YlOrRd",
    )
    fig.update_xaxes(side="top")
    return fig


def plot_dow_coverage(dow_coverage_percentage):
    fig = px.imshow(
        dow_coverage_percentage,
        title="Day of Week Coverage Percentage",
        labels=dict(x="Conflict", y="Day of Week", color="Coverage Percentage"),
        aspect="auto",
        color_continuous_scale="YlOrRd",
    )
    fig.update_xaxes(side="top")
    return fig

def plot_outlet_gini(outlet_gini):
    # Reset the index to turn conflict_name into a column
    plot_df = outlet_gini.reset_index()
    
    # Rename columns for clarity
    plot_df.columns = ['conflict_name', 'gini_coefficient']
    
    fig = px.bar(
        plot_df,
        x='conflict_name',
        y='gini_coefficient',
        title='Outlet Gini Coefficient by Conflict',
        labels={'conflict_name': 'Conflict', 'gini_coefficient': 'Gini Coefficient'},
        color='conflict_name'
    )
    fig.update_layout(showlegend=False, xaxis_tickangle=-45)
    return fig
if __name__ == "__main__":
    # Main content
    st.title("PPB Humanitarian News Coverage Analysis PoC")
    tab1, tab2 = st.tabs(["Analysis", "Documentation"])

    with tab1:
        update_dashboard()

    with tab2:
        st.header("Documentation")
        with open("doc.md", "r") as f:
            st.markdown(f.read())