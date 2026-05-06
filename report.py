import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows

print("Loading clean data...")
df = pd.read_csv('Output/clean_data.csv')
print(f"✓ Loaded {len(df)} rows")

# ================================================
# STYLES
# ================================================
header_fill = PatternFill("solid", fgColor="185FA5")
header_font = Font(bold=True, color="FFFFFF", size=11)
alt_fill    = PatternFill("solid", fgColor="E6F1FB")

def style_sheet(ws, headers):
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=col, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal='center')
    ws.freeze_panes = "A2"

wb = Workbook()

# ================================================
# SHEET 1 - KPI Summary
# ================================================
print("Creating Sheet 1 - KPI Summary...")
ws1 = wb.active
ws1.title = "KPI Summary"

kpis = [
    ["Total Orders",        df['order_id'].nunique()],
    ["Total Revenue (R$)",  round(df['price'].sum(), 2)],
    ["Avg Order Value (R$)",round(df['price'].mean(), 2)],
    ["Total Customers",     df['customer_id'].nunique()],
    ["Avg Review Score",    round(df['review_score'].mean(), 2)],
    ["Total Late Orders",   int(df['is_late'].sum())],
    ["Late Delivery Rate",  f"{df['is_late'].mean()*100:.1f}%"],
    ["Avg Delivery Days",   round(df['delivery_days'].mean(), 1)],
]

style_sheet(ws1, ["KPI Metric", "Value"])
for i, (k, v) in enumerate(kpis, 2):
    ws1.cell(row=i, column=1, value=k)
    ws1.cell(row=i, column=2, value=v)
    if i % 2 == 0:
        ws1.cell(row=i, column=1).fill = alt_fill
        ws1.cell(row=i, column=2).fill = alt_fill

ws1.column_dimensions['A'].width = 25
ws1.column_dimensions['B'].width = 20
print("✓ Sheet 1 done")

# ================================================
# SHEET 2 - Revenue by State
# ================================================
print("Creating Sheet 2 - Revenue by State...")
ws2 = wb.create_sheet("Revenue by State")

state_df = (df.groupby('customer_state')
    .agg(
        Total_Orders  = ('order_id', 'nunique'),
        Total_Revenue = ('price', 'sum'),
        Avg_Order_Value=('price', 'mean'),
        Avg_Review    = ('review_score', 'mean')
    )
    .round(2)
    .reset_index()
    .sort_values('Total_Revenue', ascending=False))

state_df.columns = ['State','Total Orders','Total Revenue (R$)',
                    'Avg Order Value','Avg Review Score']
style_sheet(ws2, list(state_df.columns))
for row in dataframe_to_rows(state_df, index=False, header=False):
    ws2.append(row)
for col in ['A','B','C','D','E']:
    ws2.column_dimensions[col].width = 20
print("✓ Sheet 2 done")

# ================================================
# SHEET 3 - Monthly Revenue Trend
# ================================================
print("Creating Sheet 3 - Monthly Trend...")
ws3 = wb.create_sheet("Monthly Trend")

monthly = (df.groupby('order_month')
    .agg(
        Total_Orders  = ('order_id', 'nunique'),
        Total_Revenue = ('price', 'sum')
    )
    .round(2)
    .reset_index())

monthly['MoM Growth %'] = (monthly['Total_Revenue']
    .pct_change()
    .mul(100)
    .round(1))

monthly.columns = ['Month','Total Orders',
                   'Total Revenue (R$)','MoM Growth %']
style_sheet(ws3, list(monthly.columns))
for row in dataframe_to_rows(monthly, index=False, header=False):
    ws3.append(row)
for col in ['A','B','C','D']:
    ws3.column_dimensions[col].width = 20
print("✓ Sheet 3 done")

# ================================================
# SHEET 4 - Delivery Analysis
# ================================================
print("Creating Sheet 4 - Delivery Analysis...")
ws4 = wb.create_sheet("Delivery Analysis")

delivery = (df.groupby('review_score')
    .agg(
        Total_Orders  = ('order_id', 'count'),
        Avg_Delivery_Days=('delivery_days', 'mean'),
        Late_Rate_Pct = ('is_late', 'mean')
    )
    .round(2)
    .reset_index())

delivery['Late_Rate_Pct'] = (delivery['Late_Rate_Pct'] * 100).round(1)
delivery.columns = ['Review Score','Total Orders',
                    'Avg Delivery Days','Late Rate %']
style_sheet(ws4, list(delivery.columns))
for row in dataframe_to_rows(delivery, index=False, header=False):
    ws4.append(row)
for col in ['A','B','C','D']:
    ws4.column_dimensions[col].width = 20
print("✓ Sheet 4 done")

# ================================================
# SAVE FILE
# ================================================
wb.save('Output/ecommerce_report.xlsx')
print("")
print("✓ Excel report saved to Output/ecommerce_report.xlsx")
print("report.py completed successfully!")