---
slug: wenzhi-domain-check
displayName: 域名是否注册查询
version: 1.0.0
summary: 批量查询 .com 等域名是否已被注册，含注册时间/注册商/到期时间/NS；无需 API Key
description: 输入一个或多个域名（或裸名 + 后缀列表），返回是否可注册、注册时间、注册商、到期时间与 NS。适合起名后快速筛可用域名、批量核对候选域名。
tags: [域名, 工具, 建站, 查询]
license: MIT
name: domain-check
metadata:
  hermes:
    tags: [域名, 建站]
---

# 域名是否注册查询

批量查域名可用性：**whois 为主 + DNS NS 兜底**，无 API Key、无调用费用。

## When to Use
- 「帮我查一下 xxx.com 有没有被注册」「这几个域名哪些能用」
- 起完名字要批量筛可用域名
- 不适用：查注册价格 / 抢注 / 商标（那是别的工具）

## 依赖
- `whois`、`dig`（不带则跑 `bash bootstrap.sh` 装）
- Python 3.8+（只用标准库）

## 用法
```bash
python3 scripts/check_domain.py example.com another.org
python3 scripts/check_domain.py mysite --tlds com,cn,ai,io     # 裸名一次查多后缀
python3 scripts/check_domain.py --json example.com             # 机器可读
python3 scripts/check_domain.py --workers 10 a.com b.com c.com # 并发
```

## 输出
| 状态 | 含义 |
|---|---|
| ✅ 未注册（可注册）| whois 返回 no match |
| ❌ 已注册 | 返回注册时间 / 注册商 / 到期 / NS |
| ⚠️ 查询失败 | 网络或 registrar 限流，可重试 |

## 坑
- 不同后缀的 whois 字段名不一样（Creation Date / Registration Time / Created On），脚本已兼容常见写法
- 部分 registrar 会限流，批量时把 `--workers` 调小（默认 6）
- `.cn` 等后缀返回中文，脚本按关键词匹配
- 网络不通时自动降级为 DNS NS 查询（有 NS ≈ 已注册）
