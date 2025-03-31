# PodTrader

## 创建策略

添加指标：选择系统指标，配置参数，完成添加；可以添加多个指标；

指标模板

```json
{
  "uniqueId": "指标唯一标识，自动生成",
  "name": "指标名称",
  "description": "指标描述",
  "interval": "数据频率，可选：1d、4h、1h、15min、5min、1min",
  "investment": {
    "symbol": "投资标的，例如：AAPL、USDJPY、YM1!",
    "secType": "投资标的类型，例如：stock, forex, future",
    "exchange": "交易所，例如：NASDAQ, FX, CBOT"
  },
  // func 和 pkg不可修改
  "func": "指标函数, 例如：'SMA'、'EMA'",
  "pkg": "指标包名, 例如：'talib'、'vectorhouse'",
  // 指标参数
  "params": [
		{
      "name": "参数名称，例如：timeperiod",
      "key": "参数，例如：timeperiod",
      "type": "参数类型，可选：int、float、str、bool",
      "value": "参数值，例如：10",
      "describe": "描述信息"
    }
  ],
  inputs: ["close"],
  outputs: ["real"]
}
```

指标列表：

```typescript
const indicatorList = [
  {
    name: 'Simple Moving Average',
    description: 'Simple Moving Average',
    package: 'talib',
    func: 'SMA',
    params: [
      {
        name: 'timeperiod',
        key: 'timeperiod',
        type: 'int',
        value: 30,
        describe: 'Number of period for the MA'
      },
      {
        name: 'matype',
        key: 'matype',
        type: 'int',
        value: 0,
        describe: 'Type of moving average'
      }
    ],
    inputs: [
      'close'
    ],
    outputs: [
      'real'
    ]
  },
  {
    name: 'Average True Range',
    description: 'Average True Range',
    package: 'talib',
    func: 'ATR',
    params: [
      {
        name: 'timeperiod',
        key: 'timeperiod',
        type: 'int',
        value: 14,
        describe: 'Number of period for the ATR'
      }
    ],
    inputs: [
      'high',
      'low',
      'close'
    ],
    outputs: [
      'real'
    ]
  },
  {
    name: 'QQE',
    description: 'QQE',
    package: 'vector-house',
    func: 'QQE',
    params: [
      {
        name: 'RSI Period',
        key: 'rsi_period',
        type: 'int',
        value: 14,
        describe: ''
      },
      {
        name: 'Smoothing Period',
        key: 'smooth',
        type: 'int',
        value: 5,
        describe: ''
      },
      {
        name: 'Factor',
        key: 'factor',
        type: 'float',
        value: 4.238,
        describe: ''
      }
    ],
    inputs: [
      'close'
    ],
    outputs: [
      'long',
      'short'
    ]
  }
]
```

添加信号：根据添加好的指标创建信号

Action可选：EQ（=）、GT（>）、GTE（>=）、LT（<）、LTE（<=）

系统数据：

- open：开盘价
- high：最高价
- low：最低价
- close：收盘价
- volume：成交量
- buy_price：买入价格
- buy_time：买入时间
- last_buy_price：上一次买入价格
- last_buy_time：上一次买入价格
- sell_price：卖出价格
- sell_time：卖出时间
- last_sell_price：上一次卖出价格
- last_sell_time：上一次卖出时间

自定义数据：手动输入的数据

指标数据：例如 IND1_SMA10.real（uniqueId + name + . + outputs）

```json
{
  "uniqueId": "唯一标识符，自动生成",
  "name": "信号名称",
  "description": "信号描述",
  "action": "操作，可选：EQ、GT、GTE、LT、LTE等",
  "source": "系统数据、自定义数据、指标数据",
  "target": "系统数据、自定义数据、指标数据",
  // 信号参数
  "params": [
    {
      name: 'Continuous Time',
      key: 'continuous_time',
      type: 'int',
      value: 1,
      describe: '持续时间'
    }
  ]
}
```

示例：

- close > buy_price + 1.8 * (IND1_Zigzag.T - IND1_Zigzag.C)

  ```json
  {
    "uniqueId": "s1",
    "name": "信号名称",
    "description": "信号描述",
    "action": "GT",
    "source": "close",
    "target": "buy_price + 1.8 * (Zigzag.T - Zigzag.C)",
    // 信号参数
    "params": [
      {
        name: 'Continuous Time',
        key: 'continuous_time',
        type: 'int',
        value: 1,
        describe: '持续时间'
      }
    ]
  }
  ```

- SMA10 > SMA20

  ```json
  {
    "uniqueId": "s1",
    "name": "信号名称",
    "description": "信号描述",
    "action": "GT",
    "source": "SMA10.real",
    "target": "SMA20.real",
    // 信号参数
    "params": [
      {
        name: 'Continuous Time',
        key: 'continuous_time',
        type: 'int',
        value: 1,
        describe: '持续时间'
      }
    ]
  }
  ```

**创建交易规则**

使用添加好的指标创建交易规则

交易规则参数模版：

```json
{
  "uniqueId": "自动生成标识符",
  "name": "交易规则名称",
  "description": "描述",
  "ruleType": "类型，可选Open、Close、StopLoss、TakeProfit",
  "action": "可选：Buy、Sell、Short",
  "expression": "交易规则表达式，例如：s1 & s2", // | & ()
  "maxFundAllocation"："最大资金分配比率，单位百分比%，默认100%"
}
```

提交回测
填写基本参数
```json
{
  "name": "策略名称",
  "description": "策略描述",
  "investment": {
    "symbol": "投资标的，例如：AAPL、USDJPY、YM1!",
    "secType": "投资标的类型，例如：stock, forex, future",
    "exchange": "交易所，例如：NASDAQ, FX, CBOT"
  },
  // 初始资金
  "initCapital": 100000,
  // 佣金
  "commission": 0.001,
  // 滑点
  "slippage": 0.001,
  "startDate": "回测开始时间",
  "endDate": "回测结束时间",
  "interval": "监控频率，可选：1d、4h、1h、15min、5min、1min"
}
```
