#!/usr/bin/env python3
"""secret_scan.py —— 发布前的隐私/密钥体检

用法：
  python3 tools/secret_scan.py                 # 扫描整个仓库（含未提交文件）
  python3 tools/secret_scan.py <目录或文件...>   # 只扫指定路径
  python3 tools/secret_scan.py --staged        # 只扫 git 暂存区（pre-commit 钩子用）

命中即 exit 1（非零），阻断提交/发布。
"""
import os, re, subprocess, sys

# 高危模式：命中即失败
PATTERNS = [
    ('skillhub Token',        r'skh_[0-9a-fA-F]{16,}'),
    ('通用 API Key/Secret',   r'(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret)\b\s*[:=]\s*[\'"][A-Za-z0-9_\-\.]{16,}[\'"]'),
    ('Bearer Token',          r'(?i)bearer\s+[A-Za-z0-9\-\._~+/]{24,}'),
    ('AWS AK',                r'\bAKIA[0-9A-Z]{16}\b'),
    ('Cloudflare/长随机串',    r'\b[A-Za-z0-9_\-]{40,}\b'),
    ('私钥内容',              r'-----BEGIN [A-Z ]*PRIVATE KEY-----'),
    ('Cookie 字段',           r'(?i)\b(sessionid|session_id|uifid|odin_tt|ms_token|passport_csrf_token)\s*='),
    ('飞书 Node/Obj Token',    r'\b(wikcn|wik|docx|doccn|nodcn)[A-Za-z0-9]{16,}\b'),
    ('飞书/Notion 页面 ID',    r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b'),
    ('邮箱地址',              r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'),
    ('本机绝对路径',           r'/home/[a-z0-9_]+/'),
    ('私有凭据目录',           r'~/\.config/hermes|~/\.venvs|~/\.h hermes'),
    ('内部域名/图床',          r'(collections\.kuwen\.top|kuwen\.top|my\.feishu\.cn/wiki|app\.notion\.com/p)'),
]
# 白名单：这些是允许出现的（公开信息/许可协议）
ALLOW = [
    r'Copyright \(c\) \d{4} wenzhi',
    r'@users\.noreply\.github\.com',       # git 提交身份（公开邮箱）
    r'example\.com|your-api\.example\.com|foo@bar',
]
SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.state'}
SKIP_EXT = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.pdf', '.zip', '.tar', '.gz', '.mp4', '.pcm', '.wav', '.pyc'}

def files_from_args(args):
    if args == ['--staged']:
        out = subprocess.run(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
                             capture_output=True, text=True).stdout
        return [f for f in out.splitlines() if f.strip()]
    if args:
        fs = []
        for a in args:
            if os.path.isdir(a):
                fs += [os.path.join(r, f) for r, d, fl in os.walk(a) for f in fl]
            else:
                fs.append(a)
        return fs
    fs = []
    for r, ds, fl in os.walk('.'):
        ds[:] = [d for d in ds if d not in SKIP_DIRS]
        fs += [os.path.join(r, f) for f in fl]
    return fs

def main():
    args = [a for a in sys.argv[1:]]
    hits = []
    for path in files_from_args(args):
        if not os.path.isfile(path): continue
        if os.path.splitext(path)[1].lower() in SKIP_EXT: continue
        if any(part in SKIP_DIRS for part in path.split(os.sep)): continue
        try:
            text = open(path, encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if any(re.search(p, line) for p in ALLOW): continue
            for name, pat in PATTERNS:
                m = re.search(pat, line)
                if m:
                    hits.append((path, i, name, m.group(0)[:60]))
    if hits:
        print('❌ 发现敏感内容，已阻断：\n')
        for p, ln, name, sample in hits:
            print(f'  [{name}] {p}:{ln}  →  {sample[:50]}…')
        print('\n处理：把值改成环境变量读取（.env 不进仓库），或从文件里删除后再提交/发布。')
        sys.exit(1)
    print('✅ 隐私体检通过：未发现 token / 密钥 / 个人 ID / 内部链接')

if __name__ == '__main__':
    main()
