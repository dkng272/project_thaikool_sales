# %%
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_processing import load_and_clean_data

#%% Plotting function
def plot_sales_by_month(df, channels=None, divisions=None, metric='Sales amount', time_period='Month', show_yoy=False):
    """
    Plot sales data by month or quarter with flexible channel and division selection
    
    Parameters:
    - df: DataFrame with sales data
    - channels: list of channels to include (None = all channels)
    - divisions: list of divisions to include (None = all divisions) 
    - metric: 'Sales amount', 'Total volume', or 'Actual sales volume'
    - time_period: 'Month' or 'Quarter'
    - show_yoy: Boolean to show Year-over-Year percentage
    """
    # Get unique values if not specified
    if channels is None:
        channels = df['Distribution channel'].unique()
    if divisions is None:
        divisions = df['Division'].unique()
    
    # Check for 'ALL' selections
    select_all_channels = 'ALL' in channels
    select_all_divisions = 'ALL' in divisions
    
    # Filter data
    if select_all_channels and select_all_divisions:
        filtered_df = df.copy()
    elif select_all_channels:
        filtered_df = df[df['Division'].isin([d for d in divisions if d != 'ALL'])].copy()
    elif select_all_divisions:
        filtered_df = df[df['Distribution channel'].isin([c for c in channels if c != 'ALL'])].copy()
    else:
        filtered_df = df[
            (df['Distribution channel'].isin(channels)) & 
            (df['Division'].isin(divisions))
        ].copy()
    
    # Add quarter column if needed
    if time_period == 'Quarter':
        filtered_df['Quarter'] = pd.PeriodIndex(filtered_df['Month'], freq='Q')
        filtered_df['Quarter'] = filtered_df['Quarter'].astype(str)
        time_col = 'Quarter'
    else:
        time_col = 'Month'
    
    # Determine grouping columns based on ALL selections
    if select_all_channels and select_all_divisions:
        # Group only by time
        grouped = filtered_df.groupby([time_col])[metric].sum().reset_index()
        grouped['Distribution channel'] = 'ALL'
        grouped['Division'] = 'ALL'
    elif select_all_channels:
        # Group by time and division
        grouped = filtered_df.groupby([time_col, 'Division'])[metric].sum().reset_index()
        grouped['Distribution channel'] = 'ALL'
    elif select_all_divisions:
        # Group by time and channel
        grouped = filtered_df.groupby([time_col, 'Distribution channel'])[metric].sum().reset_index()
        grouped['Division'] = 'ALL'
    else:
        # Group by all three dimensions
        grouped = filtered_df.groupby([time_col, 'Distribution channel', 'Division'])[metric].sum().reset_index()
    
    # Create figure
    fig = go.Figure()
    
    # If YoY is requested, calculate it
    if show_yoy:
        grouped = grouped.copy()
        grouped['Year'] = pd.to_datetime(grouped[time_col]).dt.year if time_col == 'Month' else grouped[time_col].str[:4].astype(int)
        
        # Calculate YoY for each combination
        yoy_data = []
        for channel in grouped['Distribution channel'].unique():
            for division in grouped['Division'].unique():
                subset = grouped[
                    (grouped['Distribution channel'] == channel) & 
                    (grouped['Division'] == division)
                ].copy()
                
                if not subset.empty:
                    if time_col == 'Month':
                        subset['Month_of_year'] = pd.to_datetime(subset['Month']).dt.month
                        subset['YoY'] = subset.groupby('Month_of_year')[metric].pct_change(periods=1) * 100
                    else:
                        subset['Quarter_of_year'] = subset['Quarter'].str[-1].astype(int)
                        subset['YoY'] = subset.groupby('Quarter_of_year')[metric].pct_change(periods=1) * 100
                    
                    yoy_data.append(subset)
        
        if yoy_data:
            grouped = pd.concat(yoy_data, ignore_index=True)
    
    # Add traces for each channel-division combination
    channels_to_plot = ['ALL'] if select_all_channels else [c for c in channels if c != 'ALL']
    divisions_to_plot = ['ALL'] if select_all_divisions else [d for d in divisions if d != 'ALL']
    
    for channel in channels_to_plot:
        for division in divisions_to_plot:
            data_subset = grouped[
                (grouped['Distribution channel'] == channel) & 
                (grouped['Division'] == division)
            ]
            
            if not data_subset.empty:
                # Create name based on selection
                if channel == 'ALL' and division == 'ALL':
                    trace_name = 'All Channels - All Divisions'
                elif channel == 'ALL':
                    trace_name = f'All Channels - {division}'
                elif division == 'ALL':
                    trace_name = f'{channel} - All Divisions'
                else:
                    trace_name = f'{channel} - {division}'
                
                if show_yoy:
                    # Plot YoY percentage
                    fig.add_trace(go.Scatter(
                        x=data_subset[time_col],
                        y=data_subset['YoY'],
                        mode='lines+markers',
                        name=trace_name,
                        line=dict(width=2),
                        marker=dict(size=6),
                        hovertemplate='%{x}<br>YoY: %{y:.1f}%<br>' + f'{metric}: %{{text}}<extra></extra>',
                        text=[f'{v:,.0f}' for v in data_subset[metric]]
                    ))
                else:
                    # Plot absolute values
                    fig.add_trace(go.Scatter(
                        x=data_subset[time_col],
                        y=data_subset[metric],
                        mode='lines+markers',
                        name=trace_name,
                        line=dict(width=2),
                        marker=dict(size=6)
                    ))
    
    # Update layout
    if show_yoy:
        title_text = f'{metric} - Year over Year % Change by {time_period}'
        yaxis_label = 'YoY Change (%)'
    else:
        unit = 'Billion VND' if metric == 'Sales amount' else 'Units'
        title_text = f'{metric} by {time_period}'
        yaxis_label = f'{metric} ({unit})'
    
    fig.update_layout(
        title=f'{title_text}<br><sub>Channels: {", ".join([c for c in channels if c != "ALL"])} | Divisions: {", ".join([d for d in divisions if d != "ALL"])}</sub>',
        xaxis_title=time_period,
        yaxis_title=yaxis_label,
        hovermode='x unified',
        template='plotly_white',
        height=600,
        legend=dict(
            orientation='v',
            yanchor='top',
            y=1,
            xanchor='left',
            x=1.02
        )
    )
    
    # Format y-axis
    if show_yoy:
        fig.update_yaxes(tickformat='.1f', ticksuffix='%')
    elif metric == 'Sales amount':
        fig.update_yaxes(tickformat='.1f')
    
    return fig

#%% Streamlit App
def main():
    st.set_page_config(page_title="Casper Sales Analysis", layout="wide")
    
    st.title("Casper Sales Data Analysis")
    st.markdown("---")
    
    # Load data
    @st.cache_data
    def load_data():
        return load_and_clean_data()
    
    df = load_data()
    
    # Create sidebar for filters
    st.sidebar.header("Filters")
    
    # Channel selection
    all_channels = sorted(df['Distribution channel'].unique())
    channel_options = ['ALL'] + all_channels
    selected_channels = st.sidebar.multiselect(
        "Select Channels:",
        options=channel_options,
        default=['ALL'],  # Default to ALL
        help="Select 'ALL' to sum across all channels"
    )
    
    # Division selection
    all_divisions = sorted(df['Division'].unique())
    division_options = ['ALL'] + all_divisions
    selected_divisions = st.sidebar.multiselect(
        "Select Divisions:",
        options=division_options,
        default=['ALL'],  # Default to ALL
        help="Select 'ALL' to sum across all divisions"
    )
    
    # Metric selection
    metric_options = ['Sales amount', 'Total volume', 'Actual sales volume']
    selected_metric = st.sidebar.selectbox(
        "Select Metric:",
        options=metric_options,
        index=0
    )
    
    # Time period selection
    time_period_options = ['Month', 'Quarter']
    selected_time_period = st.sidebar.radio(
        "View by:",
        options=time_period_options,
        index=0
    )
    
    # YoY option
    show_yoy = st.sidebar.checkbox(
        "Show YoY %",
        value=False,
        help="Display Year-over-Year percentage change"
    )
    
    # Main content area
    if selected_channels and selected_divisions:
        # Create and display plot
        fig = plot_sales_by_month(
            df,
            channels=selected_channels,
            divisions=selected_divisions,
            metric=selected_metric,
            time_period=selected_time_period,
            show_yoy=show_yoy
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show summary statistics
        st.markdown("### Summary Statistics")
        
        # Filter data for summary
        if 'ALL' in selected_channels and 'ALL' in selected_divisions:
            filtered_df = df.copy()
        elif 'ALL' in selected_channels:
            filtered_df = df[df['Division'].isin([d for d in selected_divisions if d != 'ALL'])].copy()
        elif 'ALL' in selected_divisions:
            filtered_df = df[df['Distribution channel'].isin([c for c in selected_channels if c != 'ALL'])].copy()
        else:
            filtered_df = df[
                (df['Distribution channel'].isin(selected_channels)) & 
                (df['Division'].isin(selected_divisions))
            ].copy()
        
        # Get only the latest period data
        if selected_time_period == 'Quarter':
            # Convert to quarter and get the latest
            filtered_df['Quarter'] = pd.PeriodIndex(filtered_df['Month'], freq='Q')
            latest_quarter = filtered_df['Quarter'].max()
            latest_data = filtered_df[filtered_df['Quarter'] == latest_quarter]
            period_label = str(latest_quarter)
            
            # Get same period last year for YoY
            if show_yoy and latest_quarter.year > filtered_df['Quarter'].min().year:
                same_quarter_last_year = pd.Period(year=latest_quarter.year - 1, quarter=latest_quarter.quarter, freq='Q')
                last_year_data = filtered_df[filtered_df['Quarter'] == same_quarter_last_year]
            else:
                last_year_data = pd.DataFrame()
        else:
            # Get the latest month
            latest_month = filtered_df['Month'].max()
            latest_data = filtered_df[filtered_df['Month'] == latest_month]
            period_label = latest_month.strftime('%B %Y')
            
            # Get same month last year for YoY
            if show_yoy and latest_month.year > filtered_df['Month'].min().year:
                same_month_last_year = latest_month - pd.DateOffset(years=1)
                last_year_data = filtered_df[
                    (filtered_df['Month'].dt.year == same_month_last_year.year) &
                    (filtered_df['Month'].dt.month == same_month_last_year.month)
                ]
            else:
                last_year_data = pd.DataFrame()
        
        # Create columns for metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            latest_sales = latest_data['Sales amount'].sum()
            if show_yoy and not last_year_data.empty:
                last_year_sales = last_year_data['Sales amount'].sum()
                yoy_change = ((latest_sales - last_year_sales) / last_year_sales * 100) if last_year_sales != 0 else 0
                st.metric(
                    f"Sales ({period_label})", 
                    f"{latest_sales:,.1f}B VND",
                    delta=f"{yoy_change:+.1f}%"
                )
            else:
                st.metric(f"Sales ({period_label})", f"{latest_sales:,.1f}B VND")
        
        with col2:
            latest_volume = latest_data['Total volume'].sum()
            if show_yoy and not last_year_data.empty:
                last_year_volume = last_year_data['Total volume'].sum()
                yoy_change = ((latest_volume - last_year_volume) / last_year_volume * 100) if last_year_volume != 0 else 0
                st.metric(
                    f"Volume ({period_label})", 
                    f"{latest_volume:,.0f} units",
                    delta=f"{yoy_change:+.1f}%"
                )
            else:
                st.metric(f"Volume ({period_label})", f"{latest_volume:,.0f} units")
        
        with col3:
            latest_actual_volume = latest_data['Actual sales volume'].sum()
            if show_yoy and not last_year_data.empty:
                last_year_actual_volume = last_year_data['Actual sales volume'].sum()
                yoy_change = ((latest_actual_volume - last_year_actual_volume) / last_year_actual_volume * 100) if last_year_actual_volume != 0 else 0
                st.metric(
                    f"Actual Volume ({period_label})", 
                    f"{latest_actual_volume:,.0f} units",
                    delta=f"{yoy_change:+.1f}%"
                )
            else:
                st.metric(f"Actual Volume ({period_label})", f"{latest_actual_volume:,.0f} units")
        
        # Show data table
        with st.expander("View Raw Data"):
            st.dataframe(
                filtered_df[['Month', 'Distribution channel', 'Division', 
                           'Sales amount', 'Total volume', 'Actual sales volume']]
                .sort_values('Month', ascending=False)
                .head(100)
            )
    else:
        st.warning("Please select at least one channel and one division.")

if __name__ == "__main__":
    main()