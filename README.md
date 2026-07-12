# 周杰伦音乐深度分析

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **跨越 26 年，16 张专辑，174 首歌曲。** 一个通过 Spotify 音频特征、歌词 NLP、
> 聚类分析和统计建模，深入探索周杰伦音乐演变的交互式数据叙事项目。

---

## 核心发现

> **《双截棍》不只是经典——它是统计上的异常值。** 能量值 0.85（前 2%）、
> 速度 106 BPM（最快 5%）、语速 0.30（前 1%），Isolation Forest 将其标记为
> 整个曲库中最"不像周杰伦"的歌曲——然而恰恰是这首歌定义了他全球性的形象。

## 项目功能

| 页面 | 解答的问题 |
|------|-----------|
| 全景 | 26 年的周杰伦音乐长什么样？ |
| 时代 | 他的音乐风格如何随年代变迁？ |
| 风格指纹 | 中国风歌曲是否有可量化的音频特征？ |
| 创作者密码 | 不同的填词人是否在歌曲上留下可测量的指纹？ |
| 歌词视角 | 歌词主题和情感如何随时间演变？ |
| 异常值 | 哪些歌曲在统计上最"不像周杰伦"？ |
| 探索器 | 自由探索和比较任意歌曲的 8 项音频特征。 |

## 展示的技能

| 领域 | 工具与技术 |
|------|-----------|
| 数据工程 | Pandas、scikit-learn 管线、数据合并与清洗 |
| 机器学习 | KMeans 聚类、PCA、Isolation Forest、随机森林 |
| 自然语言处理 | 结巴分词、TF-IDF、LDA 主题建模、情感分析 |
| 统计分析 | ANOVA、效应量、Kruskal-Wallis、事后检验 |
| 可视化 | ECharts、D3.js、雷达图、混淆矩阵、3D 散点图 |
| Web 应用 | React 18、TypeScript、Vite、Tailwind CSS |

## 交互式网站

项目包含一个完整的交互式数据叙事网站，位于 `website/` 目录：

```bash
cd website
npm install      # 安装依赖
npx vite build   # 构建生产版本
npx vite preview # 本地预览
```

网站特性：
- **Apple × Spotify Wrapped 风格** 视觉设计
- **8 个叙事章节**：首页、概览、演变、歌词、聚类、探索器、推荐、关于
- **中英文切换**：一键切换语言
- **滚动动画**：Intersection Observer 驱动的渐进式叙事
- **交互式图表**：所有 Plotly 图表支持悬停、缩放、筛选

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/ryanchangggg/jay-chou-music-analysis.git
cd jay-chou-music-analysis

# 2. 配置 Python 环境
python3 -m venv .venv
source .venv/bin/activate
make install

# 3. 运行数据管线
make data

# 4. 通过笔记本探索
make notebooks     # 启动 Jupyter Lab
```

## 项目结构

```
jay-chou-music-analysis/
├── data/
│   ├── raw/             # 原始 CSV 文件（只读）
│   └── processed/       # 预处理后的前端 JSON
├── notebooks/           # Jupyter 分析笔记本
├── src/
│   └── python/          # Python 分析包
│       ├── config.py         # 统一配置
│       ├── preprocess.py     # 数据清洗与合并
│       ├── features.py       # 特征工程
│       ├── clustering.py     # 聚类与异常检测
│       ├── lyrics.py         # 歌词 NLP（分词、LDA）
│       ├── sentiment.py      # 情感分析
│       └── stats.py          # 统计检验
├── website/             # 交互式数据叙事网站
│   ├── src/             # 源代码
│   ├── scripts/         # 数据导出脚本
│   └── dist/            # 构建输出
├── models/              # 序列化 ML 模型
├── docs/                # 文档与 PRD
├── reports/             # 生成的可视化输出
│   ├── figures/         # 交互式 HTML 图表
│   └── music_evolution_report.md
├── assets/              # 静态资源
├── Makefile             # 自动化命令
└── requirements.txt     # Python 依赖
```

## 分析方法

### 1. 音频特征分析
- 使用 Spotify Web API 采集 11 项音频特征
- PCA 降维可视化音乐空间
- UMAP 用于非线性流形学习
- KMeans 和 HDBSCAN 用于歌曲聚类

### 2. 歌词分析
- 结巴（Jieba）中文分词
- TF-IDF 关键词提取
- LDA 主题建模
- SnowNLP 情感分析

### 3. 流行度预测
- 随机森林、XGBoost、LightGBM、CatBoost 四种模型对比
- SHAP 模型解释
- 偏依赖图分析

### 4. 推荐系统
- 基于内容的协同过滤
- 余弦相似度、KNN、PCA 嵌入三种方法
- 交互式推荐 Demo

## 数据来源

- **Spotify Web API** — 音频特征（舞曲性、能量、积极度、速度、声学性等）
- **手动收集** — 歌词、专辑元数据、风格标签、专辑封面（Wikimedia Commons）

## 许可证

MIT License — 详见 [LICENSE](LICENSE)

## 致谢

- 数据通过 Spotify Web API 采集，仅用于教育分析
- 感谢周杰伦 26 年来开创性的音乐创作
- 专辑封面图片来自 Wikimedia Commons（合理使用）
