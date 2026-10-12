# skillhub-skills

老于的 AI Agent Skills 合集 —— 全部发布到 [SkillHub](https://skillhub.cn)。

## 目录结构（一个仓库，多个 skill）

```
skillhub-skills/
├── skills/                      ← 👈 所有 skill 都放这里，一个 skill 一个目录
│   ├── domain-check/            ← skill 1（目录名 = 本地标识，skillhub 上的标识是 SKILL.md 里的 slug）
│   │   ├── SKILL.md             ← 必需：说明书 + frontmatter(slug/displayName/version)
│   │   ├── scripts/             ← 这个 skill 自己的脚本
│   │   ├── bootstrap.sh         ← 装依赖（别人装了之后跑一次）
│   │   └── doctor.sh            ← 自检
│   ├── gzh-paiban/              ← skill 2（以后加的）
│   │   ├── SKILL.md
│   │   └── scripts/
│   └── ...                      ← skill 3、4、5… 无限加
├── _templates/                  ← 新建 skill 用（下划线开头，不参与发布）
│   ├── SKILL.md.template
│   └── bootstrap.sh.template
├── tools/                       ← 仓库自身的工具（不属于任何 skill）
│   └── publish_all.sh           ← 一键发布所有 skill
├── .gitignore
└── README.md
```

**关键约定**：`skills/` 下每个子目录 = 一个 skill。以后加多少个都行，互不影响。

## 新增一个 skill

```bash
mkdir -p skills/<新skill名>/scripts
cp _templates/SKILL.md.template skills/<新skill名>/SKILL.md
cp _templates/bootstrap.sh.template skills/<新skill名>/bootstrap.sh
# 填 SKILL.md（注意 slug 必须全网唯一，建议统一前缀 wenzhi-）
```

## 发布

```bash
./tools/publish_all.sh           # 预检（dry-run，只验格式，不真发）
./tools/publish_all.sh --real    # 真发布到 SkillHub
CHANGELOG="修复xxx" ./tools/publish_all.sh --real   # 自定义变更说明
```

单个发布：`skillhub publish skills/<skill名> --dry-run`

## 🛡 隐私防线（自动，不靠人记）

**每次提交、每次发布前都会自动跑 `tools/secret_scan.py` 隐私体检**：

- `.githooks/pre-commit`：`git commit` 前扫暂存区，命中密钥/隐私内容 → **直接拒绝提交**
- `tools/publish_all.sh`：发布前扫 `skills/`，不通过 → **中止发布**
- 手动随时跑：`python3 tools/secret_scan.py`

会拦截：skillhub Token（`skh_`）、API Key/Secret、Bearer Token、AKIA、私钥、cookie 字段、
飞书/Notion 页面 ID、邮箱、`/home/<用户名>/` 这类绝对路径、内部域名（图床/wiki）。

> **新克隆仓库后要启用钩子（每个克隆做一次）**：
> ```bash
> git config core.hooksPath .githooks
> ```

## 铁律

1. **绝不提交**：API Key / token / cookie / 个人 ID / 内部链接（有上面的自动体检兜底，但别故意试）
2. 每个 skill 自带 `bootstrap.sh`（装依赖）+ `doctor.sh`（自检）—— 别人装了才能跑起来
3. `slug` 全网唯一，建议统一前缀 `wenzhi-`
4. 改了 skill 就递增 `version`，发布时写 `--changelog`
