import baostock as bs
import pandas as pd
import json

print('=== Testing AShare-MCP ===')

# Test baostock with YYYY-MM-DD format
bs.login()
rs = bs.query_history_k_data_plus(
    '600519.SH',
    'date,open,high,low,close,volume',
    start_date='2025-01-01',
    end_date='2025-12-31',
    frequency='d'
)
print(f'Baostock result: error_code={rs.error_code}, error_msg={rs.error_msg}')

data = []
while rs.next():
    data.append(rs.get_row_data())
print(f'Data rows: {len(data)}')

df = pd.DataFrame(data, columns=rs.fields)
print(df.tail(3))

# Calculate indicators
close = df['close'].astype(float)
ma5 = close.rolling(5).mean().iloc[-1]
ma20 = close.rolling(20).mean().iloc[-1]

print(f'\nMA5: {ma5:.2f}')
print(f'MA20: {ma20:.2f}')

bs.logout()
print('\nTest completed successfully!')
