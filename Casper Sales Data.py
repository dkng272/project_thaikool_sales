# %%
import pandas as pd
import platform
from pathlib import Path
import plotly.graph_objects as go

#%%
def get_base_path():
    if platform.system() == 'Windows':
        return Path("G:/My Drive/Python")
    else:
        return Path("/Users/duynguyen/Library/CloudStorage/GoogleDrive-nkduy96@gmail.com/My Drive/Python")

df = pd.read_excel(get_base_path() / 'Casper Sales' / 'Sales Report by Month Raw Data.xlsx')
df.Month = pd.to_datetime(df.Month) # Make sure it's in date time format


#%% Cleaning up data and files
df = df[(~df['Distribution channel'].str.contains('total', case=False, na=False)) &
        (~df['Region'].str.contains('total', case=False, na=False)) &
        (~df['Division'].str.contains('total', case=False, na=False))
        ] # Delete all rows with 'Total' in the name (~ means exclusion)

df = df.ffill() # Front fill all the empty rows

# Fix columns names
df.rename(columns={'Sales amount \n(exclude  VAT)': 'Sales amount'}, inplace=True) # Rename for easier access
col = df.columns.str.strip() # Strip blank spaces in column names
df.columns = col # Apply the stripped names

# [df[column].dtype for column in df.columns] or df.info()

# Strip blank spaces before and after 
for column in col[1:]:
    df[column] = df[column].astype('string')
    df[column] = df[column].str.strip()
    df[column] = df[column].replace({'^-+$': '0'}, regex=True) #change "-" thành 0

for column in col[5:]: #shift back into ints for key numbers
   df[column] = df[column].astype('float64')   

# Chia sales amount về tr
df['Sales amount'] = df['Sales amount'] / (10**9)
    
# Edit product types and divisions
df['Division'] = df['Division'].replace({'Other': 'Others'}) # Fix 'Others' and 'Other'
df['Division'] = df['Division'].replace({'Washing machine': 'Washing Machine'}) # Fix 'Washing Machine' 
df['Division'] = df['Division'].replace({'Tivi' : 'Television'}) # Fix 'Television'

# Edit product types
df['Type of product'] = df['Type of product'].replace({'Small Size' : 'Small size', 'Large Size' : 'Large size', 'Large sie' : 'Large size'}) #fixed TV
df['Type of product'] = df['Type of product'].replace({'Multi door' : 'Multi doors', 'Multil door' : 'Multi doors', 'Refrigerator, Side by Side' : 'Side by Side'}) #fixed fridge
df['Type of product'] = df['Type of product'].replace({'Air vented dryer, 7KG, non-inverter' : 'Dryer Machine', 'Dryer' : 'Dryer Machine'}) # fixed WM+
# All types of heater + fan + purifier 
df['Type of product'] = df['Type of product'].replace({'Water Purifier' : 'Water purifier'}) 
df['Type of product'] = df['Type of product'].replace({'Electric Fan' : 'Electric fan'}) 
df['Type of product'] = df['Type of product'].replace({'Air Purifier' : 'Air purifier'}) 
df['Type of product'] = df['Type of product'].replace({'Induction Headting' : 'Induction Heating'}) 
df['Type of product'] = df['Type of product'].replace({'Direct Water Heater' : 'Water Heater'}) 
df['Type of product'] = df['Type of product'].replace({'Indirect Water Heater' : 'Water Heater'}) 
df['Type of product'] = df['Type of product'].replace({'Induction Heating' : 'Water Heater'}) 
# All type of cookers turn into just Cooker
df['Type of product'] = df['Type of product'].replace({'Rice Cooker' : 'Cooker'}) 
df['Type of product'] = df['Type of product'].replace({'Electric rice cooker' : 'Cooker'}) 
df['Type of product'] = df['Type of product'].replace({'Induction cooker' : 'Cooker'}) 
df['Type of product'] = df['Type of product'].replace({'Electric cooker' : 'Cooker'}) 
df['Type of product'] = df['Type of product'].replace({'Induction rice cooker' : 'Cooker'}) 

# Edit channel names (post 2025 changes)
df['Distribution channel'] = df['Distribution channel'].replace({'Channel GT' : 'GT', 'Channel MT' : 'MT', 'Khách lẻ' : 'Retail', 'Others' : 'Others', 'ECOM' : 'ECOM'})

# Merge some other divisions
df['Division'] = df['Division'].replace({'Others - SDA': 'Others', 'Others - SHA': 'Others'})


#%% Save as csv for safety
df.to_csv(get_base_path() / 'Casper Sales' / 'Sales Data_cleaned.csv', index=False)

#%%
# # Create relevant lists
# channel = ['Channel GT', 'Channel MT', 'Khách lẻ', 'Others']
# region = ['North', 'South', 'Middle']
# division = ['CAC', 'RAC', 'Washing Machine', 'Television', 'Refrigerator', 'Others']


# %%
# Tính divisions và theo kênh
summary = df.groupby(['Division','Region','Month'])[['Total volume','Actual sales volume','Sales amount']].sum().reset_index()
by_products = df.groupby(['Division','Month'])[['Total volume','Actual sales volume','Sales amount']].sum().reset_index()
by_channel = df.groupby(['Distribution channel','Division','Month'])[['Total volume','Actual sales volume','Sales amount']].sum().reset_index()

#%% Plotting tool
def plot_sales_by_month(df, channels=None, divisions=None, metric='Sales amount'):
    """
    Plot sales data by month with flexible channel and division selection
    
    Parameters:
    - df: DataFrame with sales data
    - channels: list of channels to include (None = all channels)
    - divisions: list of divisions to include (None = all divisions) 
    - metric: 'Sales amount', 'Total volume', or 'Actual sales volume'
    """
    # Get unique values if not specified
    if channels is None:
        channels = df['Distribution channel'].unique()
    if divisions is None:
        divisions = df['Division'].unique()
    
    # Filter data
    filtered_df = df[
        (df['Distribution channel'].isin(channels)) & 
        (df['Division'].isin(divisions))
    ]
    
    # Group by month and aggregate
    grouped = filtered_df.groupby(['Month', 'Distribution channel', 'Division'])[metric].sum().reset_index()
    
    # Create figure
    fig = go.Figure()
    
    # Add traces for each channel-division combination
    for channel in channels:
        for division in divisions:
            data_subset = grouped[
                (grouped['Distribution channel'] == channel) & 
                (grouped['Division'] == division)
            ]
            
            if not data_subset.empty:
                fig.add_trace(go.Scatter(
                    x=data_subset['Month'],
                    y=data_subset[metric],
                    mode='lines+markers',
                    name=f'{channel} - {division}',
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
    
    # Update layout
    unit = 'Billion VND' if metric == 'Sales amount' else 'Units'
    fig.update_layout(
        title=f'{metric} by Month<br><sub>Channels: {", ".join(channels)} | Divisions: {", ".join(divisions)}</sub>',
        xaxis_title='Month',
        yaxis_title=f'{metric} ({unit})',
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
    if metric == 'Sales amount':
        fig.update_yaxes(tickformat='.1f')
    
    return fig

#%% Example usage
# Basic plot with all channels and divisions
fig1 = plot_sales_by_month(df)
fig1.show()

# Plot specific channels and divisions
fig2 = plot_sales_by_month(
    df, 
    channels=['GT', 'MT'], 
    divisions=['CAC', 'RAC', 'Refrigerator']
)
fig2.show()

# Plot with different metric - Total volume
fig3 = plot_sales_by_month(
    df,
    channels=['ECOM', 'Retail'],
    divisions=['Television', 'Washing Machine'],
    metric='Total volume'
)
fig3.show()

# Plot with actual sales volume
fig4 = plot_sales_by_month(
    df,
    channels=['GT', 'MT', 'ECOM'],
    divisions=['CAC', 'RAC'],
    metric='Actual sales volume'
)
fig4.show()
