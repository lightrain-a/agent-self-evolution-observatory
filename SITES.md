# Agent / RSI 两个研究网站的构建与切换

## 当前发布结构

| 逻辑网站 | 现有访问入口 | 内容和左侧菜单 | 独立构建产物 |
| --- | --- | --- | --- |
| Agent Self-Evolution Observatory | https://agent-evolution.lightrain.asia/ | Agent 研究全景、系统、论文与实验；`data.js` 中只包含 Agent 导航 | `_site/` 根目录 |
| RSI Self-Improvement Observatory | https://agent-evolution.lightrain.asia/rsi/ | RSI 综述、I5、方法、实验和可拓展的论文阅读卡片；`rsi/site-nav.js` 单独供给导航 | `_site/rsi/` 完整独立静态站 |

这是**两个相互跳转、分别构建的逻辑网站**。目前仍使用**同一个自定义域名与一个 GitHub Pages 部署**；不是已经配置了两个 DNS 域名或两套 GitHub Pages 仓库。

两侧边栏最上方都有 Agent / RSI 切换。切换地址分别是 `/` 和 `/rsi/`，不会将原有 Agent URL 搬迁，也不会破坏 `/rsi/*.html` 的旧深链接。

## 生产构建

```bash
# 第一步：构建 Agent 网站及其附属静态数据。会清空并重建 _site/
python3 scripts/build_static_site.py

# 第二步：由结构化 RSI 源生成独立 HTML 和 site-nav.js
python3 scripts/build_rsi_research.py

# 第三步：仅构建 RSI 网站，将页面和独立的运行时资源放到 _site/rsi/
python3 scripts/build_rsi_site.py

# 检查两站导航和资源边界
python3 scripts/test_rsi_site.py
python3 scripts/test_rsi_browser.py
```

GitHub Actions 的 `.github/workflows/pages.yml` 按同样顺序构建并将组合后的 `_site/` 发布到 Pages。由于 Agent 构建会重建 `_site/`，本流水线必须先 Agent、后 RSI。两个构建器的**代码、运行时导航与页面入口分离**，但部署仍由统一的 Pages workflow 原子发布。

## 单独打包 RSI

```bash
python3 scripts/build_rsi_research.py
python3 scripts/build_rsi_site.py --output _rsi-standalone
```

`_rsi-standalone` 具备自己的 `index.html`、`site-nav.js`、`research.js`、`site-base.css`、`site-switch.css`、`favicon.svg` 和搜索数据，不请求 Agent 的 `data.js`、`style.css` 等资源。其跨站按钮当前仍指向同域路径；如果将来发布在 `rsi.example.org`，要同时改为**两站的实际绝对 URL**，并单独配置 DNS / TLS / Pages，不能假定路径在另一个域名下仍有效。

## 新增论文阅读卡片

仅编辑 `rsi/reading-cards.json`，追加一个 `papers` 条目，然后运行 `python3 scripts/build_rsi_research.py`。卡片渲染、RSI 侧边导航、站内搜索保持自动化，Agent 导航不受影响。

## 回滚与兼容性

本改动保留旧的根目录 Agent 页面和全部已有 RSI 页面路径；没有改动研究、论文或实验内容。切换入口由 Agent 站 `app.js`（独立页面 `advisor-review.html` 静态实现）以及 RSI 页面生成器分别控制。改动需要时可通过 Git 提交整体回滚。
