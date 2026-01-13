# Claude API 速度测试报告

**测试时间**: 2026-01-14
**API 地址**: http://43.160.243.8:8000
**测试内容**: 首字时间 (TTFT) 和生成速度 (Token/s)

## 可用模型列表

- claude-sonnet-4-20250514
- claude-sonnet-4-5-20250929
- claude-opus-4-5-20251101
- claude-haiku-4-5
- claude-haiku-4-5-20251001

## 测试结果

| 模型 | 首字时间 (TTFT) | Token/s |
|------|----------------|---------|
| claude-sonnet-4-20250514 | 3.8 - 5.3s | 21 - 25 |
| claude-sonnet-4-5-20250929 | 5.1 - 7.0s | 25 - 27 |
| claude-opus-4-5-20251101 | 6.7 - 6.8s | 20 - 22 |
| claude-haiku-4-5 | 4.1 - 8.3s | 23 - 71 |
| claude-haiku-4-5-20251001 | 4.2 - 7.4s | 42 - 226 |

## 分析

### 首字时间 (TTFT)
- 整体在 4-8 秒之间
- 波动较大，与服务器负载相关
- Opus 模型首字时间相对稳定

### 生成速度 (Token/s)
- Haiku 模型最快，峰值可达 200+ token/s
- Sonnet 和 Opus 模型稳定在 20-27 token/s
- 速度波动较大，服务端可能存在队列机制

### 稳定性
- 偶尔出现 502 错误
- 服务端存在间歇性问题

## 测试脚本

测试脚本: `test_api_speed_temp.py`

运行方式:
```bash
python test_api_speed_temp.py
```
