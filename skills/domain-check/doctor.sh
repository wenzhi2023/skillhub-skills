#!/usr/bin/env bash
# 自检：依赖是否齐、能否真的查到结果
fails=0
for c in whois dig python3; do
  if command -v $c >/dev/null; then echo "✅ $c"; else echo "❌ 缺少 $c（跑 bash bootstrap.sh）"; fails=$((fails+1)); fi
done
echo "--- 实测一次 google.com ---"
if command -v whois >/dev/null; then
  whois google.com 2>/dev/null | grep -qi "domain name" && echo "✅ whois 查询正常" || { echo "❌ whois 查不到（网络/被限流）"; fails=$((fails+1)); }
fi
echo
[ "$fails" = 0 ] && echo "🎉 环境就绪" || echo "⚠️ 有 $fails 项待处理"
exit $fails
