#!/usr/bin/env python3
"""check_domain.py —— 批量查域名是否已注册（免费 skill）

用法：
  python3 check_domain.py example.com another.org
  python3 check_domain.py mysite --tlds com,cn,ai,io        # 一次查多个后缀
  python3 check_domain.py --json example.com                # 机器可读输出

原理：whois（主）+ DNS NS 查询（兜底）。无需 API Key、无调用费用。
"""
import argparse, json, re, subprocess, sys, concurrent.futures as cf

def run(cmd, timeout=20):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout or ''
    except Exception:
        return ''

def whois_check(domain, timeout=20):
    """返回 (状态, 详情dict)；状态: registered / available / unknown"""
    out = run(['whois', domain], timeout)
    if not out:
        return 'unknown', {'reason': 'whois 无响应'}
    low = out.lower()
    if re.search(r'no match|not found|no data found|no entries found|status: free', low):
        return 'available', {}
    info = {}
    def grab(label, pat, flags=re.I):
        m = re.search(pat, out, flags)
        return m.group(1).strip() if m else ''
    info['registrar'] = grab('registrar', r'^\s*Registrar:\s*(.+)$', re.I | re.M)
    info['created'] = grab('created', r'^\s*(?:Creation Date|Created On|Registration Time|Domain Registration Date):\s*(.+)$', re.I | re.M)
    info['expires'] = grab('expires', r'^\s*(?:Registry Expiry Date|Expiration Date|Expiration Time|Registrar Registration Expiration Date):\s*(.+)$', re.I | re.M)
    ns = re.findall(r'^\s*Name Server:\s*(.+)$', out, re.I | re.M)
    info['ns'] = [n.strip().lower() for n in ns][:4]
    if any(info.values()) or re.search(r'\bdomain name:\b', low):
        return 'registered', info
    return 'unknown', {'reason': 'whois 输出无法识别'}

def dns_check(domain, timeout=10):
    """兜底：有 NS 记录 → 几乎必然已注册"""
    out = run(['dig', '+short', 'NS', domain], timeout)
    ns = [l.strip() for l in out.splitlines() if l.strip()]
    return ('registered', {'ns': ns[:4]}) if ns else ('unknown', {})

def check(domain):
    domain = domain.strip().lower().lstrip('http://').lstrip('https://').split('/')[0]
    status, info = whois_check(domain)
    if status == 'unknown':
        s2, i2 = dns_check(domain)
        if s2 != 'unknown':
            status, info = s2, i2
        else:
            info = {**info, **i2}
    return {'domain': domain, 'status': status, **info}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('names', nargs='+', help='域名，或裸名（配合 --tlds）')
    ap.add_argument('--tlds', default='', help='后缀列表，如 com,cn,ai（把裸名补全成完整域名）')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--workers', type=int, default=6)
    a = ap.parse_args()

    domains = []
    for n in a.names:
        if a.tlds and '.' not in n:
            domains += [f'{n}.{t.strip().lstrip(".")}' for t in a.tlds.split(',') if t.strip()]
        else:
            domains.append(n)

    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        results = list(ex.map(check, domains))

    if a.json:
        print(json.dumps(results, ensure_ascii=False, indent=1))
        return
    icon = {'available': '✅ 未注册（可注册）', 'registered': '❌ 已注册', 'unknown': '⚠️ 查询失败'}
    print(f'{"域名":<32}{"状态":<22}备注')
    print('-' * 78)
    for r in results:
        note = r.get('registrar') or ''
        if r.get('created'):
            note += f' | 注册于 {r["created"][:10]}'
        if r.get('ns'):
            note += f' | NS {r["ns"][0]}'
        if r.get('reason'):
            note = r['reason']
        print(f'{r["domain"]:<32}{icon[r["status"]]:<22}{note}')
    ok = sum(1 for r in results if r['status'] == 'available')
    print(f'\n共 {len(results)} 个：未注册 {ok} 个，已注册 {sum(1 for r in results if r["status"]=="registered")} 个')

if __name__ == '__main__':
    main()
