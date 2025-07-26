import pandas as pd

print("reading")

xls = pd.ExcelFile("/Users/sakshi/Downloads/Data-&-Problem-Statement---Project----1/Credit Banking_Project - 1.xls")
print(xls)


# Load and clean each sheet
customer_df = xls.parse('Customer Acqusition')
spend_df = xls.parse('Spend')
repayment_df = xls.parse('Repayment')

# Standardize column names
def clean_columns(df):
    df.columns = df.columns.str.strip().str.replace(':', '').str.replace(' ', '_')
    return df

customer_df = clean_columns(customer_df)
spend_df = clean_columns(spend_df).rename(columns={'Costomer': 'Customer'})
repayment_df = clean_columns(repayment_df).rename(columns={'Costomer': 'Customer'})

print("Spend columns:", spend_df.columns.tolist())
print("Repayment columns:", repayment_df.columns.tolist())

# Convert data types
customer_df['Limit'] = customer_df['Limit'].replace('[₹,]', '', regex=True).astype(float)
customer_df['Age'] = pd.to_numeric(customer_df['Age'], errors='coerce')
spend_df['Amount'] = pd.to_numeric(spend_df['Amount'], errors='coerce')
repayment_df['Amount'] = pd.to_numeric(repayment_df['Amount'], errors='coerce')

# Option 1: Replace with median age
median_age = customer_df[customer_df['Age'] >= 18]['Age'].median()
customer_df.loc[customer_df['Age'] < 18, 'Age'] = median_age

# task-1-> Monthly Spend per Customer
monthly_spend = spend_df.groupby(['Customer', 'Month'])['Amount'].sum().reset_index()
monthly_spend.rename(columns={'Amount': 'Monthly_Spend'}, inplace=True)

#task-2-> Monthly Repayment per Customer
monthly_repayment = repayment_df.groupby(['Customer', 'Month'])['Amount'].sum().reset_index()
monthly_repayment.rename(columns={'Amount': 'Monthly_Repayment'}, inplace=True)

# Merge with customer limits
spend_with_limit = monthly_spend.merge(customer_df[['Customer', 'Limit']], on='Customer', how='left')
overspenders = spend_with_limit[spend_with_limit['Monthly_Spend'] > spend_with_limit['Limit']]

#task-3-> Highest Paying 10 Customers (by repayment)
total_repayment = monthly_repayment.groupby('Customer')['Monthly_Repayment'].sum().reset_index()
top_10_payers = total_repayment.sort_values(by='Monthly_Repayment', ascending=False).head(10)

#task-4-> Segment Spending Analysis
# Merge spend with customer segment
spend_with_segment = monthly_spend.merge(customer_df[['Customer', 'Segment']], on='Customer', how='left')
segment_spending = spend_with_segment.groupby('Segment')['Monthly_Spend'].sum().reset_index()

#task-5-> Age Group Spending Analysis

def age_group(age):
    if age < 25:
        return '18-24'
    elif age < 35:
        return '25-34'
    elif age < 45:
        return '35-44'
    elif age < 55:
        return '45-54'
    else:
        return '55+'

customer_df['Age_Group'] = customer_df['Age'].apply(age_group)
spend_with_age = monthly_spend.merge(customer_df[['Customer', 'Age_Group']], on='Customer', how='left')
age_spending = spend_with_age.groupby('Age_Group')['Monthly_Spend'].sum().reset_index()

#task-6-> Most Profitable Segment
# Merge spend and repayment
merged = monthly_spend.merge(monthly_repayment, on=['Customer', 'Month'], how='left')
merged['Monthly_Repayment'] = merged['Monthly_Repayment'].fillna(0)
merged['Outstanding'] = merged['Monthly_Spend'] - merged['Monthly_Repayment']
merged['Interest'] = merged['Outstanding'].apply(lambda x: x * 0.029 if x > 0 else 0)

# Add Segment info
merged = merged.merge(customer_df[['Customer', 'Segment']], on='Customer', how='left')
segment_profit = merged.groupby('Segment')['Interest'].sum().reset_index()
segment_profit.rename(columns={'Interest': 'Total_Profit'}, inplace=True)

#task7-> Category-wise Spending (from Spend "Type")
category_spending = spend_df.groupby('Type')['Amount'].sum().reset_index().sort_values(by='Amount', ascending=False)

#task-8-> 
monthly_summary = pd.merge(
    monthly_spend,
    monthly_repayment,
    on=['Customer', 'Month'],
    how='left'
)

# Replace missing repayments with 0
monthly_summary['Monthly_Repayment'] = monthly_summary['Monthly_Repayment'].fillna(0)

# Calculate due amount
monthly_summary['Due_Amount'] = monthly_summary['Monthly_Spend'] - monthly_summary['Monthly_Repayment']

# Interest of 2.9% only if due > 0
monthly_summary['Interest'] = monthly_summary['Due_Amount'].apply(lambda x: x * 0.029 if x > 0 else 0)


#task-9-> Monthly Profit Calculation
monthly_profit = merged.groupby(['Month'])['Interest'].sum().reset_index()

# final output preview
print("Monthly Spend:\n", monthly_spend.head())
print("Monthly Repayment:\n", monthly_repayment.head())
print("Top 10 Payers:\n", top_10_payers)
print("Segment Spending:\n", segment_spending)
print("Age Group Spending:\n", age_spending)
print("Segment Profit:\n", segment_profit)
print("Top Categories:\n", category_spending)
print("After imposing interest rate of 2.9 for each customer for any due amount\n",monthly_summary.head())
print("Monthly Bank Profit:\n", monthly_profit)






















