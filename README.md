# 喜鹊礼簿（Magpie Gift Ledger）

> 一款专注「婚礼礼金记账 + 人情往来管理」的小程序。吉祥物 **阿喜**（衔红包的小喜鹊，喜鹊报喜）陪你记好每一份心意。

当前已实现 **基础版（免费版）** 的前端（uni-app 小程序 / H5）、后端（FastAPI）与数据库（SQLite）。升级版、高级版规划见 [`docs/PRODUCT.md`](docs/PRODUCT.md)。

![阿喜](assets/ip/axi-mascot.svg)

---

## 目录结构

```
graft_write/
├── assets/ip/            # 吉祥物「阿喜」IP 设计源文件（SVG）
├── backend/              # FastAPI + SQLite 后端
│   └── app/
│       ├── main.py       # 入口、CORS、路由注册
│       ├── models.py     # ORM 模型（账本/礼金/实物/提醒）
│       ├── schemas.py    # Pydantic 校验
│       ├── security.py   # 密码锁哈希（PBKDF2）
│       └── routers/      # gifts / items / reminders / stats / lock / blessings
├── frontend/             # uni-app（Vue3 + TS），可编译为微信小程序 / H5
│   └── src/pages/        # index / add / stats / remind / items / mine / lock
└── docs/PRODUCT.md       # 三版本产品规划与商业化方案
```

## 基础版功能（已实现）

- **多渠道礼金登记**：现金 / 微信 / 支付宝；记录姓名、关系、事由、备注、日期，金额快捷预设。
- **基础账目管理**：单笔增删改查；**防重复录入提醒**；按 亲戚 / 朋友 / 同事 / 家人 分组筛选。
- **基础数据统计**：收礼总额、各渠道汇总、按关系分组、最高金额；一键复制账单摘要分享。
- **基础提醒 & 祝福**：自定义节点提醒（生日 / 节日 / 喜事）；内置由「阿喜」呈现的祝福语模板，填入称呼一键复制。
- **隐私与权限**：单账号、4–6 位账本密码锁（PBKDF2 哈希存储，绝不明文）。
- **简易实物登记**：文字记录礼品名称、赠送人、数量（拍照识别为升级版功能）。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | uni-app（Vue 3 + TypeScript + Vite），一套代码编译微信小程序 / H5 |
| 后端 | FastAPI + Uvicorn |
| 数据库 | SQLite（SQLAlchemy 2.0 ORM） |

---

## 本地运行

### 1. 后端

```bash
cd backend
pip install -e ".[dev]"          # 安装依赖
python -m uvicorn app.main:app --reload --port 8000
```

接口文档：http://localhost:8000/docs

### 2. 前端（H5，便于浏览器调试）

```bash
cd frontend
npm install
npm run dev:h5                    # 默认连后端 http://localhost:8000
```

打开 http://localhost:5173/ 即可。如需指定后端地址：

```bash
VITE_API_BASE=https://your-api.example.com npm run build:h5
```

### 3. 前端（微信小程序）

```bash
cd frontend
npm run build:mp-weixin           # 产物在 dist/build/mp-weixin
```

用微信开发者工具导入 `dist/build/mp-weixin` 目录即可预览。小程序环境下请在
`src/config.ts` 中将 `API_BASE` 指向已部署的后端 HTTPS 域名（并在小程序后台配置
request 合法域名）。

## 测试

```bash
cd backend
pytest                            # 后端 API 测试
```

## 商业化与版本规划

详见 [`docs/PRODUCT.md`](docs/PRODUCT.md)：基础版（免费引流）→ 升级版（轻 AI，主流付费）→ 高级版（全功能 + 现场互动，高端 / 商用）。
