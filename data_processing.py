# %%
import pandas as pd
from pathlib import Path

#%%
def load_and_clean_data():
    """Load raw data and perform all cleaning operations"""
    # Use relative path - looks for file in the same directory as this script
    current_dir = Path(__file__).parent
    df = pd.read_excel(current_dir / 'Sales Report by Month Raw Data.xlsx')
    df.Month = pd.to_datetime(df.Month) # Make sure it's in date time format
    
    # Cleaning up data and files
    df = df[(~df['Distribution channel'].str.contains('total', case=False, na=False)) &
            (~df['Region'].str.contains('total', case=False, na=False)) &
            (~df['Division'].str.contains('total', case=False, na=False))
            ] # Delete all rows with 'Total' in the name (~ means exclusion)
    
    df = df.ffill() # Front fill all the empty rows
    
    # Fix columns names
    df.rename(columns={'Sales amount \n(exclude  VAT)': 'Sales amount'}, inplace=True) # Rename for easier access
    col = df.columns.str.strip() # Strip blank spaces in column names
    df.columns = col # Apply the stripped names
    
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

    # Save as csv for safety
    df.to_csv(current_dir / 'Sales Data_cleaned.csv', index=False)
    
    return df


#%% Main execution
if __name__ == "__main__":
    df = load_and_clean_data()
    print("Data processing completed. Cleaned data saved to 'Sales Data_cleaned.csv'")
    print(f"Data shape: {df.shape}")
    print(f"Date range: {df['Month'].min()} to {df['Month'].max()}")