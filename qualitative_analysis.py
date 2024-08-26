import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def load_qualitative_data():
    sentiment_shift = pd.read_csv("results/normalized_sentiment_shift_monthly.csv")
    entity_counts = pd.read_csv("results/normalized_entity_counts_monthly.csv")
    coverage_analysis = pd.read_csv("results/normalized_coverage_analysis_monthly.csv")
    leaders_mentions = pd.read_csv("results/normalized_leaders_mentions_monthly.csv")
    # co_occurrence = pd.read_csv("results/normalized_co_occurrence_monthly.csv")

    # Convert month to datetime
    for df in [sentiment_shift, entity_counts, coverage_analysis, leaders_mentions]:
        df['month'] = pd.to_datetime(df['month'])

    return sentiment_shift, entity_counts, coverage_analysis, leaders_mentions

def apply_filters(df, selected_outlets, selected_conflicts, date_range):
    filtered_df = df[
        (df['outlet_name'].isin(selected_outlets)) &
        (df['conflict_name'].isin(selected_conflicts)) &
        (df['month'] >= pd.Timestamp(date_range[0])) &
        (df['month'] <= pd.Timestamp(date_range[1]))
    ]
    return filtered_df

def plot_sentiment_shift(sentiment_shift, selected_outlets, selected_conflicts, date_range):
    filtered_df = apply_filters(sentiment_shift, selected_outlets, selected_conflicts, date_range)
    
    fig = go.Figure()
    
    for conflict in selected_conflicts:
        conflict_data = filtered_df[filtered_df['conflict_name'] == conflict]
        fig.add_trace(go.Scatter(
            x=conflict_data['month'],
            y=conflict_data['normalized_sentiment_score'],
            mode='lines',
            name=conflict
        ))
    
    fig.update_layout(
        title="Normalized Sentiment Shift Over Time by Conflict",
        xaxis_title="Month",
        yaxis_title="Normalized Sentiment Score",
        legend_title="Conflict"
    )
    
    return fig

def plot_entity_counts(entity_counts, selected_outlets, selected_conflicts, date_range):
    filtered_df = apply_filters(entity_counts, selected_outlets, selected_conflicts, date_range)
    
    if len(selected_conflicts) == 1:
        # If only one conflict is selected, create a single bar chart
        conflict_data = filtered_df[filtered_df['conflict_name'] == selected_conflicts[0]]
        top_entities = conflict_data.groupby('entity_name')['normalized_count'].sum().nlargest(10)
        
        fig = go.Figure(go.Bar(x=top_entities.index, y=top_entities.values, name=selected_conflicts[0]))
        
        fig.update_layout(
            title=f"Top 10 Mentioned Entities for {selected_conflicts[0]} (Normalized)",
            xaxis_title="Entity",
            yaxis_title="Normalized Count",
            height=500
        )
        fig.update_xaxes(tickangle=45)
        
    else:
        # If two or more conflicts are selected, create subplots
        fig = make_subplots(rows=1, cols=len(selected_conflicts), subplot_titles=selected_conflicts)
        
        for i, conflict in enumerate(selected_conflicts, start=1):
            conflict_data = filtered_df[filtered_df['conflict_name'] == conflict]
            top_entities = conflict_data.groupby('entity_name')['normalized_count'].sum().nlargest(10)
            
            fig.add_trace(
                go.Bar(x=top_entities.index, y=top_entities.values, name=conflict),
                row=1, col=i
            )
        
        fig.update_layout(
            title="Top 10 Mentioned Entities by Conflict (Normalized)",
            height=500,
            showlegend=False
        )
        fig.update_xaxes(title_text="Entity", tickangle=45)
        fig.update_yaxes(title_text="Normalized Count")
    
    return fig

def plot_coverage_analysis(coverage_analysis, selected_outlets, selected_conflicts, date_range):
    filtered_df = apply_filters(coverage_analysis, selected_outlets, selected_conflicts, date_range)
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                        subplot_titles=("Death Reporting", "Human Rights Violations"))
    
    for conflict in selected_conflicts:
        conflict_data = filtered_df[filtered_df['conflict_name'] == conflict]
        
        fig.add_trace(go.Scatter(
            x=conflict_data['month'],
            y=conflict_data['normalized_death_report'],
            mode='lines',
            name=f"{conflict} - Death Reporting"
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=conflict_data['month'],
            y=conflict_data['normalized_hr_violation'],
            mode='lines',
            name=f"{conflict} - HR Violations"
        ), row=2, col=1)
    
    fig.update_layout(
        title="Normalized Coverage of Death Reporting and Human Rights Violations by Conflict",
        height=700
    )
    fig.update_xaxes(title_text="Month", row=2, col=1)
    fig.update_yaxes(title_text="Normalized Count", row=1, col=1)
    fig.update_yaxes(title_text="Normalized Count", row=2, col=1)
    
    return fig

def plot_leaders_mentions(leaders_mentions, selected_outlets, selected_conflicts, date_range):
    filtered_df = apply_filters(leaders_mentions, selected_outlets, selected_conflicts, date_range)
    contexts = filtered_df['context'].unique()
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=selected_conflicts)
    
    for i, conflict in enumerate(selected_conflicts, start=1):
        conflict_data = filtered_df[filtered_df['conflict_name'] == conflict]
        
        for context in contexts:
            context_data = conflict_data[conflict_data['context'] == context]
            fig.add_trace(
                go.Bar(
                    x=context_data['leader'],
                    y=context_data['normalized_mention_count'],
                    name=context,
                    text=context_data['normalized_mention_count'].round(2),
                    textposition='auto'
                ),
                row=1, col=i
            )
    
    fig.update_layout(
        title="Normalized Leaders Mentions by Context and Conflict",
        height=500,
        barmode='group'
    )
    fig.update_xaxes(title_text="Leader", tickangle=45)
    fig.update_yaxes(title_text="Normalized Mention Count")
    
    return fig

def plot_co_occurrence(co_occurrence, selected_outlets, selected_conflicts, date_range):
    filtered_df = apply_filters(co_occurrence, selected_outlets, selected_conflicts, date_range)
    co_occurrence_types = [col for col in filtered_df.columns if col.startswith('normalized_co_occurrence')]
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=selected_conflicts)
    
    for i, conflict in enumerate(selected_conflicts, start=1):
        conflict_data = filtered_df[filtered_df['conflict_name'] == conflict]
        
        for co_type in co_occurrence_types:
            fig.add_trace(
                go.Scatter(
                    x=conflict_data['month'],
                    y=conflict_data[co_type],
                    mode='lines',
                    name=co_type.replace('normalized_co_occurrence_', '')
                ),
                row=1, col=i
            )
    
    fig.update_layout(
        title="Normalized Co-occurrence Over Time by Conflict",
        height=500
    )
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Normalized Co-occurrence Count")
    
    return fig