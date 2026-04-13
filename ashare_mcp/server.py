"""
AShare-MCP - A股量化交易 MCP 服务器
"""
import json
import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

__version__ = "1.0.0"

# ==================== 数据获取模块 ====================

class StockDataFetcher:
    """股票数据获取器"""

    def get_kline(
        self,
        symbol: str,
        period: str = "daily",
        start_date: str = None,
        end_date: str = None,
        adjustflag: str = "2"
    ) -> Dict[str, Any]:
        """获取K线数据"""
        bs.login()

        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

        freq_map = {"daily": "d", "weekly": "w", "monthly": "m"}
        freq = freq_map.get(period, "d")

        rs = bs.query_history_k_data_plus(
            symbol,
            "date,open,high,low,close,volume,amount,adjustflag",
            start_date=start_date,
            end_date=end_date,
            frequency=freq,
            adjustflag=adjustflag
        )

        if rs.error_code != '0':
            bs.logout()
            return {"error": f"查询失败: {rs.error_msg}"}

        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())

        bs.logout()

        if not data_list:
            return {"error": f"未获取到 {symbol} 的数据"}

        df = pd.DataFrame(data_list, columns=rs.fields)
        return {
            "symbol": symbol,
            "period": period,
            "data": df.to_dict(orient='records'),
            "count": len(df)
        }

    def get_indicators(
        self,
        symbol: str,
        end_date: str = None,
        period: str = "daily"
    ) -> Dict[str, Any]:
        """计算技术指标"""
        kline_data = self.get_kline(symbol, period=period, end_date=end_date)

        if "error" in kline_data:
            return kline_data

        df = pd.DataFrame(kline_data["data"])

        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        close = df['close']
        results = {"symbol": symbol}

        if len(close) >= 5:
            results["ma5"] = round(float(close.rolling(5).mean().iloc[-1]), 2)
        if len(close) >= 10:
            results["ma10"] = round(float(close.rolling(10).mean().iloc[-1]), 2)
        if len(close) >= 20:
            results["ma20"] = round(float(close.rolling(20).mean().iloc[-1]), 2)
        if len(close) >= 60:
            results["ma60"] = round(float(close.rolling(60).mean().iloc[-1]), 2)

        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = (ema12 - ema26) * 2
        signal = macd.ewm(span=9).mean()
        results["macd"] = round(float(macd.iloc[-1]), 3)
        results["macd_signal"] = round(float(signal.iloc[-1]), 3)
        results["macd_hist"] = round(float((macd - signal).iloc[-1]), 3)

        if len(close) >= 14:
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs_val = gain / loss
            rsi = 100 - (100 / (1 + rs_val))
            results["rsi"] = round(float(rsi.iloc[-1]), 2)

        if len(close) >= 20:
            mid = close.rolling(20).mean()
            std = close.rolling(20).std()
            results["boll_upper"] = round(float((mid + 2 * std).iloc[-1]), 2)
            results["boll_middle"] = round(float(mid.iloc[-1]), 2)
            results["boll_lower"] = round(float((mid - 2 * std).iloc[-1]), 2)

        results["latest_close"] = round(float(close.iloc[-1]), 2)
        results["latest_date"] = df['date'].iloc[-1] if 'date' in df.columns else None

        return results

    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        bs.login()
        rs = bs.query_stock_basic(code=symbol)
        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())
        bs.logout()

        if not data_list:
            return {"error": f"未获取到 {symbol} 的信息"}

        return {"symbol": symbol, "data": data_list[0] if data_list else None}


# ==================== MCP 协议处理 ====================

@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: Dict[str, Any]


class AShareMCPServer:
    """AShare MCP 服务器"""

    def __init__(self):
        self.data_fetcher = StockDataFetcher()
        self.tools = self._create_tools()

    def _create_tools(self) -> List[MCPTool]:
        """创建工具清单"""
        return [
            MCPTool(
                name="get_stock_kline",
                description="获取A股K线数据，支持日/周/月线",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码，如 '600519.SH' 或 '000001.SZ'"
                        },
                        "period": {
                            "type": "string",
                            "enum": ["daily", "weekly", "monthly"],
                            "description": "K线周期",
                            "default": "daily"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "开始日期 YYYY-MM-DD"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "结束日期 YYYY-MM-DD"
                        }
                    },
                    "required": ["symbol"]
                }
            ),
            MCPTool(
                name="get_technical_indicators",
                description="获取技术指标，包括均线、MACD、RSI、布林带",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码，如 '600519.SH'"
                        },
                        "period": {
                            "type": "string",
                            "enum": ["daily", "weekly", "monthly"],
                            "description": "K线周期",
                            "default": "daily"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "结束日期 YYYY-MM-DD"
                        }
                    },
                    "required": ["symbol"]
                }
            ),
            MCPTool(
                name="get_stock_info",
                description="获取股票基本信息",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码，如 '600519.SH'"
                        }
                    },
                    "required": ["symbol"]
                }
            )
        ]

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理 MCP 请求"""
        method = request.get("method")
        request_id = request.get("id")

        if method == "tools/list":
            return self._handle_list_tools(request_id)
        elif method == "tools/call":
            return self._handle_call_tool(request_id, request.get("params", {}))
        elif method == "initialize":
            return self._handle_initialize(request_id, request.get("params", {}))
        elif method == "notifications/initialized":
            return {"jsonrpc": "2.0"}
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Unknown method: {method}"},
                "id": request_id
            }

    def _handle_initialize(self, request_id, params) -> Dict[str, Any]:
        """处理初始化请求"""
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "AShare-MCP", "version": __version__}
            },
            "id": request_id
        }

    def _handle_list_tools(self, request_id) -> Dict[str, Any]:
        """处理工具列表请求"""
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.input_schema
                    }
                    for tool in self.tools
                ]
            },
            "id": request_id
        }

    def _handle_call_tool(self, request_id, params) -> Dict[str, Any]:
        """处理工具调用请求"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "get_stock_kline":
                result = self.data_fetcher.get_kline(**arguments)
            elif tool_name == "get_technical_indicators":
                result = self.data_fetcher.get_indicators(**arguments)
            elif tool_name == "get_stock_info":
                result = self.data_fetcher.get_stock_info(**arguments)
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": f"Unknown tool: {tool_name}"},
                    "id": request_id
                }

            if isinstance(result, dict) and "error" in result:
                content = [{"type": "text", "text": result["error"]}]
            else:
                content = [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

            return {"jsonrpc": "2.0", "result": {"content": content}, "id": request_id}

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "result": {"content": [{"type": "text", "text": f"Error: {str(e)}"}]},
                "id": request_id
            }


def mcp_run():
    """运行 MCP 服务器（stdio 模式）"""
    import sys
    server = AShareMCPServer()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = server.handle_request(request)
            if response:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": None}), flush=True)


if __name__ == "__main__":
    mcp_run()
