# AShare-MCP

<div align="center">

**A Stock Quantitative Trading MCP Server**

*基于 Baostock 数据源的 A股量化交易 MCP 服务器*

[![PyPI Version](https://img.shields.io/pypi/v/ashare-mcp.svg)](https://pypi.org/project/ashare-mcp/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)

</div>

---

## 📖 简介

AShare-MCP 是一个开源的 A股量化交易 MCP (Model Context Protocol) 服务器，基于 Baostock 免费数据源，让 AI 助手（如 Trae、Claude、Cursor）能够直接调用 A股技术分析和量化数据。

## ✨ 特性

- 🚀 **一键部署**：pip install 后即可使用
- 📊 **完整数据**：支持沪深两市所有股票
- 📈 **技术指标**：MACD、RSI、布林带、均线等
- 🤖 **MCP 协议**：原生支持 AI 助手调用
- 🔧 **可扩展**：支持自定义技术指标
- 💰 **完全免费**：使用 Baostock 免费数据源

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AI 助手 (Trae/Claude/Cursor)            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ MCP Protocol
┌─────────────────────────────────────────────────────────────┐
│                      AShare-MCP Server                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ get_kline   │  │ get_indicators│ │ get_stock_info│       │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Baostock 数据源                          │
│                   (免费 A股数据)                             │
└─────────────────────────────────────────────────────────────┘
```

## 📦 安装

### 方式一：pip 安装

```bash
pip install ashare-mcp
```

### 方式二：从源码安装

```bash
git clone https://github.com/aitrados/ashare-mcp.git
cd ashare-mcp
pip install -e .
```

## 🚀 快速开始

### 方式一：命令行运行

```bash
# 直接运行 MCP 服务器
ashare-mcp

# 或
python -m ashare_mcp
```

### 方式二：在 Python 中使用

```python
from ashare_mcp import AShareMCPServer

server = AShareMCPServer()

# 获取K线数据
result = server.data_fetcher.get_kline(
    symbol="600519.SH",
    period="daily",
    start_date="2026-01-01",
    end_date="2026-04-13"
)
print(result)
```

## 🛠️ MCP 工具列表

| 工具 | 说明 | 参数 |
|------|------|------|
| `get_stock_kline` | 获取K线数据 | symbol, period, start_date, end_date |
| `get_technical_indicators` | 获取技术指标 | symbol, period, end_date |
| `get_stock_info` | 获取股票基本信息 | symbol |
| `get_realtime_quote` | 获取实时行情 | symbol |

## 📊 支持的技术指标

| 类别 | 指标 |
|------|------|
| 均线系统 | MA5, MA10, MA20, MA60 |
| MACD | DIF, DEA, MACD柱 |
| 动量指标 | RSI(14) |
| 布林带 | 上轨, 中轨, 下轨 |

## 🔧 Trae/Claude 配置

### Trae Desktop 配置

在 Trae 设置中添加 MCP 服务器：

```json
{
  "mcpServers": {
    "ashare-mcp": {
      "command": "ashare-mcp",
      "args": []
    }
  }
}
```

### Claude Desktop 配置

在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "ashare-mcp": {
      "command": "python",
      "args": ["-m", "ashare_mcp"]
    }
  }
}
```

## 📝 使用示例

### 在 Trae 中使用

```
用户: 帮我分析贵州茅台(600519)的最新走势

Trae 调用:
1. get_stock_kline(symbol="600519.SH") → 获取K线数据
2. get_technical_indicators(symbol="600519.SH") → 获取技术指标

返回:
- 均线系统状态
- MACD 金叉/死叉信号
- RSI 超买/超卖判断
- BOLL 突破/回调信号
```

### Python API 示例

```python
from ashare_mcp import AShareMCPServer

server = AShareMCPServer()

# 获取技术指标
indicators = server.data_fetcher.get_indicators(
    symbol="600519.SH",
    period="daily"
)

print(f"最新收盘价: {indicators['latest_close']}")
print(f"MA5: {indicators['ma5']}")
print(f"MA20: {indicators['ma20']}")
print(f"MACD: {indicators['macd']}")
print(f"RSI: {indicators['rsi']}")
print(f"BOLL: {indicators['boll_upper']}/{indicators['boll_middle']}/{indicators['boll_lower']}")
```

## 📁 项目结构

```
ashare-mcp/
├── README.md
├── LICENSE
├── pyproject.toml
├── ashare_mcp/
│   ├── __init__.py
│   └── server.py        # MCP 服务器核心
└── tests/
    └── test_server.py   # 测试
```

## 🔌 数据源

- **Baostock**：免费 A股数据（主要）
- **AkShare**：备用数据源

## 📋 系统要求

- Python 3.8+
- 网络连接（获取数据）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 致谢

- [Baostock](http://www.baostock.com/) - 免费 A股数据源
- [AkShare](https://github.com/akfamily/akshare) - 财经数据接口
- [finance-trading-ai-agents-mcp](https://github.com/aitrados/finance-trading-ai-agents-mcp) - 参考项目

---

<div align="center">

**如果这个项目对你有帮助，请点个 Star ⭐**

</div>
