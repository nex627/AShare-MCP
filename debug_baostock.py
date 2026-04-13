import baostock as bs
import pandas as pd
from ashare_mcp.server import AShareMCPServer
import json

print('=== Test 1: AShareMCPServer ===')
server = AShareMCPServer()
result = server.data_fetcher.get_indicators('600519.SH', period='daily')
print(json.dumps(result, indent=2, ensure_ascii=False))
print('\nTest completed!')
