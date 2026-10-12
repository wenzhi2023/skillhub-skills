#!/usr/bin/env bash
# 一键发布 skills/ 下所有 skill 到 SkillHub（默认 dry-run 预检）
# 用法： ./tools/publish_all.sh            # 预检，不真发
#        ./tools/publish_all.sh --real     # 真发布
#        CHANGELOG="修复 xxx" ./tools/publish_all.sh --real
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${SKILLHUB_HOST:-https://api.skillhub.cn}"
REAL=0
[ "${1:-}" = "--real" ] && REAL=1

found=0; ok=0; bad=0
while IFS= read -r d; do
  name="${d#$ROOT/skills/}"
  echo "──────── $name ────────"
  if [ "$REAL" = "1" ]; then
    if skillhub publish "$d" --host "$HOST" --changelog "${CHANGELOG:-更新}"; then ok=$((ok+1)); else bad=$((bad+1)); fi
  else
    if skillhub publish "$d" --host "$HOST" --dry-run; then ok=$((ok+1)); else bad=$((bad+1)); fi
  fi
  found=$((found+1))
done < <(find "$ROOT/skills" -name SKILL.md -printf '%h\n' | sort)

echo
echo "共 $found 个 skill：成功 $ok / 失败 $bad"
[ "$REAL" = "1" ] && echo "（已真实发布）" || echo "（仅预检；真发布加 --real）"
exit $([ "$bad" = 0 ] && echo 0 || echo 1)
