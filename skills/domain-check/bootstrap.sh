#!/usr/bin/env bash
# 安装依赖：whois + dig
set -e
echo "检查 whois / dig ..."
miss=""
command -v whois >/dev/null || miss="$miss whois"
command -v dig   >/dev/null || miss="$miss dnsutils"
if [ -n "$miss" ]; then
  echo "缺少：$miss"
  if command -v apt-get >/dev/null; then
    sudo apt-get update -qq && sudo apt-get install -y $miss
  elif command -v brew >/dev/null; then
    brew install $(echo $miss | sed 's/dnsutils/bind/')
  else
    echo "请手动安装：$miss"; exit 1
  fi
fi
echo "✅ 依赖就绪：$(whois -V 2>/dev/null | head -1 || echo whois) / $(dig -v 2>&1 | head -1)"
