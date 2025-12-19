# EduInsight 慧教通

<div align="center">
[![Vue 3](https://img.shields.io/badge/Vue-3.5.22-4FC08D?style=flat&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9.0-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Ant Design](https://img.shields.io/badge/Ant%20Design-4.2.6-0170FE?style=flat&logo=ant-design&logoColor=white)](https://antdv.com/)

</div>

基于 **Vue 3 + Flask + AI** 的现代化教学管理平台，提供资料管理、考勤管理、成绩管理、课堂互动等功能，并集成智能资料归类和学情预警预测。

## 主要功能

- **用户认证**：多角色登录（管理员/教师/学生）、权限控制
- **资料中心**：文件上传下载、在线预览、智能分类、全文搜索
- **考勤管理**：二维码签到、考勤统计、报表导出
- **成绩管理**：成绩录入、统计分析、可视化图表、Excel 导入导出
- **课堂互动**：实时投票、在线提问、弹幕互动
- **智能归类**：基于 NLP 的文档自动分类和标签推荐（准确率 85%+）
- **学情预测**：基于机器学习的成绩预测和风险预警（准确率 75%+）

## 技术栈

### 前端

![Vue.js](https://img.shields.io/badge/Vue.js-3.5.22-4FC08D?style=flat&logo=vue.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9.0-3178C6?style=flat&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-7.1.11-646CFF?style=flat&logo=vite&logoColor=white)
![Ant Design](https://img.shields.io/badge/Ant%20Design-4.2.6-0170FE?style=flat&logo=ant-design&logoColor=white)
![Pinia](https://img.shields.io/badge/Pinia-3.0.3-FFD859?style=flat&logo=pinia&logoColor=black)
![ECharts](https://img.shields.io/badge/ECharts-6.0.0-AA344D?style=flat&logo=apache-echarts&logoColor=white)

### 后端

![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?style=flat&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-3.1.1-D71F00?style=flat&logo=sqlalchemy&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2.4.2-E92063?style=flat&logo=pydantic&logoColor=white)

### 数据库与部署

![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat&logo=mysql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-1.25-009639?style=flat&logo=nginx&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-21.2.0-499848?style=flat&logo=gunicorn&logoColor=white)

### AI 算法

![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.2-F7931E?style=flat&logo=scikit-learn&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.26.2-013243?style=flat&logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.1.4-150458?style=flat&logo=pandas&logoColor=white)

## 快速启动

### 方式一：Docker 一键部署（推荐）

```bash
# Windows
docker-start.bat

# Linux/Mac
chmod +x docker-start.sh
./docker-start.sh
```

启动后访问：

- 前端：http://localhost:5173
- 后端 API：http://localhost:5030
- API 文档：http://localhost:5030/openapi/swagger

### 方式二：本地开发

#### 后端启动

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
copy .env.example .env          # Windows
# cp .env.example .env          # Linux/Mac

python init_db.py               # 初始化数据库
python run.py                   # 启动后端（http://localhost:5030）
```

#### 前端启动

```bash
cd frontend
npm install
npm run openapi2ts              # 生成 API 类型（需后端已启动）
npm run dev                     # 启动前端（http://localhost:5173）
```

## 项目结构

```
EduInsight/
├── backend/                # 后端代码
│   ├── app/               # 应用主目录
│   │   ├── api/          # API 接口
│   │   ├── models/       # 数据模型
│   │   ├── schemas/      # 数据验证
│   │   └── services/     # 业务逻辑
│   ├── init_db.py        # 数据库初始化
│   └── run.py            # 启动文件
├── frontend/              # 前端代码
│   ├── src/
│   │   ├── api/          # API 调用
│   │   ├── components/   # 组件
│   │   ├── pages/        # 页面
│   │   ├── stores/       # 状态管理
│   │   └── router/       # 路由配置
│   └── package.json
├── docs/                  # 项目文档
├── docker-compose.yml     # Docker 编排
└── README.md
```

## 开发规范

- 后端优先开发，完成后运行 `npm run openapi2ts` 生成前端类型
- 遵循 [模型与 Schema 定义规范](.kiro/steering/model-schema-definition-rules.md)
- 提交代码前确保通过测试和代码检查

## License

MIT License
