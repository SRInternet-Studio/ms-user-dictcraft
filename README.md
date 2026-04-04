# MS User DictCraft

**MS User DictCraft** 是一款为 Windows 微软拼音输入法打造的高效词库管理与生成工具，旨在通过简化的 GUI 界面和批量化处理能力，帮助用户快速构建、管理和转换自定义词库（.dat格式），打破输入法的词汇瓶颈。

无论是**教育工作者**管理学生姓名，还是**专业人士**整理术语表、**游戏玩家**导入快捷短语，DictCraft 都能助你一臂之力。

## ✨ 核心特点

*   **一键批量生成**：支持从 TXT 文件导入列表，秒级生成大量词条。
*   **多模式拼音引擎**：内置首字母、首字全拼、全拼等多种智能转换策略。
*   **智能位置分配**：自动检测并处理重复拼音的冲突，确保词库准确导入。
*   **现代化 GUI 界面**：基于现代主题设计，操作直观，支持深色模式。
*   **高效词库构建**：将结构化数据直接编译为 Microsoft 输入法原生的 `.dat` 格式。
*   **灵活数据管理**：通过可视化表格编辑器，轻松进行增删改查。

## 🚀 快速上手

### 1. 环境准备
*   操作系统：Windows 10/11
*   Python 环境：Python 3.8+

### 2. 安装与运行
```bash
# 1. 克隆仓库
git clone https://github.com/SRInternet-Studio/ms-user-dictcraft.git
cd ms-user-dictcraft

# 2. 安装必要依赖
pip install -r requirements.txt

# 3. 运行程序
python main.py
```

## 📖 使用指南

1. **批量构建**：在“批量生成”标签页中导入文本文件，设置好拼音规则与词条参数，一键生成。
2. **精细编辑**：在“词条编辑”标签页中，像操作 Excel 一样管理你的词条数据。
3. **导出词库**：在“生成词典”标签页，选择保存路径，即可获得可直接导入输入法的 `.dat` 文件。
4. **导入微软输入法**：
   * 打开 `设置 > 时间和语言 > 语言和区域 > 中文（简体） > 选项`。
   * 找到“微软拼音”设置，进入“词库和自学习”。
   * 点击“导入词典”，选择生成的 `.dat` 文件即可生效。

## 🛠 技术栈
*   **GUI 框架**：Tkinter (优化版)
*   **数据处理**：Pandas
*   **中文处理**：pypinyin
*   **界面美化**：sv-ttk, pywinstyles

## 🧩 项目结构

```
ms-user-dictcraft/
├── main.py          # 主程序文件，包含GUI界面实现
├── lib/             # 核心库
│   ├── user_dict.py # 词典处理类，负责.dat文件的读写和解析
│   └── utils.py     # 工具函数，提供十六进制字符串转换功能
├── sources/         # 资源文件
│   ├── HarmonyOS_Sans_SC_Regular.ttf # 字体文件
│   └── app.png      # 应用图标
├── dict.csv         # 词条数据文件，存储所有词条信息
├── requirements.txt # 依赖文件
├── README.md        # 说明文档
└── 分析.md          # .dat文件格式分析文档
```

## 🏗 二次开发

### 核心模块说明

1. **UserDict 类** (`lib/user_dict.py`)
   - 负责处理.dat文件的读写和解析
   - 主要方法：
     - `add_item(pinyin, phrase, i_candidate, sql_key)`: 添加词条
     - `to_bytes()`: 将词典转换为二进制数据
     - `to_dat_file(file_path)`: 保存为.dat文件
     - `from_dat_file(file_path)`: 从.dat文件加载

2. **GUI 模块** (`main.py`)
   - 实现了三个主要标签页：
     - 生成词典：用于生成DAT文件
     - 词条编辑：用于管理词条
     - 批量生成：用于从TXT文件批量生成词条
     - 关于：显示项目信息

3. **数据存储**
   - 使用CSV文件 (`dict.csv`) 存储词条数据
   - 字段包括：符号、中文名、英文名、拼音、位置、描述

### 扩展功能

1. **添加新的拼音生成方式**
   - 在 `generate_pinyin` 方法中添加新的生成逻辑
   - 在批量生成标签页中添加对应的选项

2. **支持更多文件格式**
   - 扩展 `browse_txt` 方法，支持其他格式文件的读取
   - 添加文件格式转换功能

3. **增加数据导入/导出功能**
   - 添加从其他词典格式导入的功能
   - 支持导出为其他格式

4. **优化界面**
   - 增加暗黑模式支持
   - 优化响应式布局

如果您有任何好的功能建议或 Bug 反馈，欢迎提交 **Pull Request** 或开启 **Issue**。

## 📜 协议与致谢

*   **协议**：本项目基于 MIT 协议开源。
*   **致谢**：核心逻辑参考并使用了 [MS User Dictionary Toolkit](https://github.com/Louisredstone/ms-user-dict-toolkit)，在此向原作者表示感谢。

---

**联系我们** | [官网](https://www.sr-studio.cn) | srinternet@qq.com