# MED 环境数据平台

Django开发的环境数据展示平台，提供空气质量数据可视化和用户管理功能。

## 快速开始

### 启动项目

```bash
# 激活虚拟环境
med_env\Scripts\activate

# 启动服务器
python manage.py runserver
```

访问 http://127.0.0.1:8000

## 页面功能详细介绍

### 🏠 首页系列
- **`index.html`** - 平台主页：展示平台介绍、产品卡片、用户导航入口
- **`index_backup.html`** - 主页备份版本：保留历史版本，用于回滚参考

### 🔐 用户认证系列
- **`sign_in.html`** - 用户登录页：邮箱密码登录、记住登录状态、跳转注册
- **`login.html`** - 备用登录页：简化版登录界面，功能与sign_in.html类似
- **`sign_up.html`** - 用户注册页：新用户注册、邮箱验证、密码确认

### 📧 邮箱验证系列  
- **`verify_email.html`** - 邮箱验证页面：用户点击邮件链接后的验证确认页
- **`verify_email_new.html`** - 新版邮箱验证：改进UI的邮箱验证页面
- **`verification_sent.html`** - 验证邮件发送确认：提示用户检查邮箱的中间页面

### 👤 用户状态管理
- **`user_status.html`** - 用户状态页：显示当前登录状态、个人信息、权限等级

### 🗂️ 数据下载系列（重点区分）
- **`data_download.html`** - **主数据下载页**：完整功能的数据下载中心
  - 支持多地区（中国、英国）数据选择
  - 多种污染物类型筛选（PM2.5、PM10、NO2、O3等）
  - 时间范围选择（年月日）
  - 批量下载和单个文件下载
  - 下载统计和使用记录
  
- **`data_download-single.html`** - **单文件下载页**：简化版下载页面
  - 针对单个数据集的下载
  - 简化的筛选选项
  - 快速下载流程
  
- **`data_download_1.0.html`** - **1.0版本下载页**：早期版本的数据下载页
  - 保留旧版功能逻辑
  - 用于版本对比和功能回滚

### 🗺️ 地图可视化系列（重点区分）
- **`data_echart.html`** - **ECharts数据地图**：基于ECharts的数据可视化
  - 使用ECharts图表库
  - 重点在统计图表展示
  - 柱状图、饼图等数据分析
  
- **`data_echart_map.html`** - **ECharts交互地图**：ECharts + 地图的综合页面
  - 结合ECharts和地图组件
  - 地图上的数据点可视化
  - 支持图表和地图联动
  
- **`data_echart_map_unfinished.html`** - **未完成的ECharts地图**：开发中版本
  - 功能尚未完善
  - 用于开发测试
  
- **`data_local_map.html`** - **本地数据地图**：用户上传本地数据的地图展示
  - 支持用户上传JSON格式的空气质量数据
  - Leaflet地图展示自定义数据
  - 本地文件解析和可视化
  - 污染物类型切换（PM2.5、PM10、O3、NO2、SO2、CO）
  
- **`data_local_map_unfinished.html`** - **未完成的本地地图**：开发中版本

### 🛠️ 工具页面
- **`data_fetch_tool.html`** - **数据获取工具**：数据抓取和处理工具页面
  - API数据获取接口
  - 数据格式转换
  - 批量数据处理

### 🧠 模型展示
- **`model_instruction.html`** - **模型介绍页**：AI模型和算法展示
  - 2×3网格展示6种环境数据模型
  - PM2.5、PM10、臭氧、NO2、温度、紫外辐射预测模型
  - 模态框详细介绍每个模型的技术规格
  - 模型概述、技术方法、应用领域说明

### 🧭 导航组件
- **`navbar.html`** - **导航栏组件**：可重用的顶部导航栏
  - 统一的网站导航
  - 用户登录状态显示
  - 响应式设计

### 页面对比总结

#### 数据下载页面差异：
- `data_download.html`：**功能最全面**，支持复杂筛选和批量操作
- `data_download-single.html`：**单一功能**，专注单文件快速下载  
- `data_download_1.0.html`：**历史版本**，保留早期功能逻辑

#### 地图页面差异：
- `data_echart.html`：**纯图表**，无地图组件
- `data_echart_map.html`：**图表+预设地图**，展示固定数据源
- `data_local_map.html`：**地图+用户数据**，支持上传自定义数据

#### 登录页面差异：
- `sign_in.html`：**主登录页**，功能完整，UI精美
- `login.html`：**备用登录页**，简化版本

#### 邮箱验证差异：
- `verify_email.html`：**标准版本**
- `verify_email_new.html`：**改进版本**，更好的用户体验
- `verification_sent.html`：**发送确认页**，引导用户下一步操作

## 快速导航表

| 功能需求 | 推荐模板文件 | 备选方案 | 说明 |
|---------|-------------|----------|------|
| 🏠 **网站首页** | `index.html` | `index_backup.html` | 主页备份版本 |
| 🔐 **用户登录** | `sign_in.html` | `login.html` | 简化版登录页 |
| 📝 **用户注册** | `sign_up.html` | - | 完整注册流程 |
| 📧 **邮箱验证** | `verify_email_new.html` | `verify_email.html` | 新版UI更优 |
| 📊 **完整数据下载** | `data_download.html` | `data_download_1.0.html` | 功能最全面 |
| ⚡ **快速下载** | `data_download-single.html` | - | 单文件下载 |
| 🗺️ **固定数据地图** | `data_echart_map.html` | - | 31城市空气质量 |
| 📁 **自定义数据地图** | `data_local_map.html` | - | 用户上传数据 |
| 📈 **纯图表展示** | `data_echart.html` | - | ECharts统计图 |
| 🧠 **AI模型介绍** | `model_instruction.html` | - | 6种预测模型 |
| 👤 **用户状态** | `user_status.html` | - | 账户信息页 |
| 🛠️ **数据工具** | `data_fetch_tool.html` | - | API获取工具 |

## 模板文件开发指南

### 📊 模板文件统计
- **总计模板数量**：20+ 个HTML文件
- **核心业务页面**：8个（首页、登录、注册、数据下载、地图展示、模型介绍等）
- **功能变体页面**：7个（不同版本的下载页、地图页、登录页）
- **辅助功能页面**：5个（邮箱验证、用户状态、工具页面等）

### 🛠️ 新页面开发流程
1. 在 `med_platform/templates/` 创建新的HTML文件
2. 继承基础模板或使用include组件
3. 在 `main_app/views.py` 添加对应视图函数
4. 在 `main_app/urls.py` 配置访问路由
5. 测试页面功能和响应式效果

### 📝 页面命名规范
- **主功能页面**：使用简洁名称（如 `data_download.html`）
- **功能变体**：添加描述后缀（如 `data_download-single.html`）
- **版本迭代**：添加版本号（如 `data_download_1.0.html`）
- **开发中页面**：添加 `_unfinished` 后缀
- **备份页面**：添加 `_backup` 后缀

### 🎯 选择合适的页面模板
- **需要完整下载功能**：使用 `data_download.html`
- **需要简单快速下载**：使用 `data_download-single.html`
- **需要展示固定数据地图**：使用 `data_echart_map.html`
- **需要用户上传数据地图**：使用 `data_local_map.html`
- **需要纯数据图表展示**：使用 `data_echart.html`

## 项目特色

- **空气质量地图**: 31个主要城市的实时空气质量数据可视化
- **数据下载**: 多种格式的环境数据文件下载
- **用户系统**: 注册、登录、权限管理
- **响应式设计**: 适配桌面和移动设备

## 技术实现

- Django 4.2 + SQLite
- Leaflet.js 地图可视化
- MiSans 字体
- 自适应CSS布局

## 项目结构

```
med-platform/
├── manage.py
├── requirements.txt
├── med_platform/          # 项目配置
│   ├── settings.py
│   ├── urls.py
│   └── templates/         # 页面模板
├── main_app/              # 主应用
│   ├── models.py          # 数据模型
│   ├── views.py           # 业务逻辑
│   └── urls.py            # 路由配置
├── staticfiles/           # 静态资源
│   └── air-quality-data.json
├── fonts/                 # 字体文件
└── image/                 # 图片资源
```

## 开发

### 数据库操作

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 修改页面

1. 编辑 `med_platform/templates/` 中的HTML文件
2. 在 `main_app/views.py` 添加视图函数
3. 在 `main_app/urls.py` 配置路由

### 空气质量数据

编辑 `staticfiles/air-quality-data.json` 文件修改地图显示的城市数据。

## 部署

生产环境需要修改 `settings.py`：

```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
```

然后收集静态文件：

```bash
python manage.py collectstatic
```

## 核心页面功能详述

### 🏠 首页（/ - index.html）
**平台门户和导航中心**
- 展示MED环境数据平台的核心定位和品牌形象
- 三大数据产品卡片：中国环境数据、英国环境数据、全球环境数据
- 产品卡片包含详细的数据类型说明（PM2.5、PM10、NO2、O3、温度、紫外辐射、NDVI等）
- 响应式设计，支持桌面和移动设备访问
- 用户认证状态显示，已登录用户显示邮箱和注销选项

### 🔐 用户认证页面

#### 登录（/sign-in/ - sign_in.html）
**主要用户登录入口**
- 邮箱 + 密码登录方式
- 记住登录状态功能
- 登录失败错误提示
- 快速跳转注册页面链接
- 统一的UI设计风格

#### 注册（/sign-up/ - sign_up.html）  
**新用户注册中心**
- 用户基本信息填写（邮箱、密码、确认密码）
- 实时表单验证（邮箱格式、密码强度、重复邮箱检测）
- 注册成功后自动跳转登录或直接登录
- 邮箱验证流程集成

### 📧 邮箱验证流程
- **verification_sent.html**：验证邮件发送确认页，引导用户检查邮箱
- **verify_email.html**：标准邮箱验证页面，用户点击邮件链接后的确认页
- **verify_email_new.html**：改进版邮箱验证，更优的用户体验设计

### 📊 数据下载中心（核心功能区别说明）

#### 主数据下载页（/data-download/ - data_download.html）
**功能最完整的数据下载中心**
- **多地区支持**：中国、英国、全球数据
- **丰富数据类型**：PM2.5、粗颗粒物、PM10、NO2、O3、SO2、CO、温度、紫外辐射、NDVI、夜光等
- **精确时间筛选**：支持年（2023）、月（2023-07）、日（2023-07-15）级别筛选
- **多种文件格式**：CSV、Excel、JSON等主流格式下载
- **批量下载功能**：支持选择多个数据集批量下载
- **下载统计显示**：每个数据集的下载次数和热度
- **详细数据说明**：数据来源、更新频率、空间分辨率、数据质量等信息
- **用户下载历史**：已登录用户的下载记录追踪

#### 单文件下载页（data_download-single.html）
**简化版快速下载**
- 专注单个数据文件的快速下载
- 简化的筛选界面，减少用户选择复杂度
- 适合明确知道所需数据的用户
- 更快的页面加载速度

#### 1.0版本下载页（data_download_1.0.html）
**历史版本保留**
- 保留早期版本的功能逻辑
- 用于版本对比和功能回滚
- 开发调试时的参考版本

### 🗺️ 地图可视化系统（重点功能区分）

#### ECharts数据地图（/data-echart/ - data_echart.html）
**纯统计图表展示**
- 基于ECharts图表库的数据可视化
- 柱状图、饼图、折线图等多种图表类型
- 重点在统计数据的图形化展示
- 无地理地图组件，专注数据分析

#### ECharts交互地图（/data-echart-map/ - data_echart_map.html）  
**预设数据的地图可视化**
- 结合ECharts和Leaflet地图组件
- 展示31个主要城市的固定空气质量数据
- 实时AQI、PM2.5、PM10、O3、NO2、SO2、CO指标切换
- 城市标记点击显示详细污染物浓度
- 颜色编码的空气质量等级显示（优、良、轻度污染等）
- 自动数据更新和时间戳显示
- 适合政府部门、科研机构的监测需求

#### 本地数据地图（/data-local-map/ - data_local_map.html）
**用户自定义数据可视化**
- 支持用户上传本地JSON格式的空气质量数据
- Leaflet地图展示用户自定义数据点
- 文件格式验证和数据解析
- 污染物类型自由切换（PM2.5、PM10、O3、NO2、SO2、CO）
- ECharts统计图表与地图联动显示
- 适合研究人员分析自己的数据集
- 数据隐私保护（本地处理，不上传服务器）

### 🧠 AI模型展示（/model-instruction/ - model_instruction.html）
**环境数据模型科普中心**
- 2×3网格布局展示6种核心环境预测模型
- **PM2.5预测模型**：机器学习算法、1km分辨率、R²>0.85
- **PM10预测模型**：深度学习CNN、多源卫星数据融合
- **臭氧浓度模型**：光化学生成机理、OMI卫星数据
- **NO2浓度模型**：TROPOMI/OMI卫星、交通排放源
- **地表温度模型**：MODIS热红外、气象站观测融合
- **紫外辐射模型**：大气参数、6S辐射传输模式
- 每个模型点击后弹出详细模态框，包含技术规格、应用领域、验证精度
- 适合学术研究、技术交流、科普教育

### 🛠️ 辅助功能页面

#### 用户状态页（user_status.html）
- 显示当前用户的登录状态、个人信息
- 账户权限等级和功能权限显示
- 用户活动历史和数据使用统计

#### 数据获取工具（data_fetch_tool.html）
- 提供API数据获取接口
- 数据格式转换工具
- 批量数据处理功能
- 适合开发者和高级用户

#### 管理后台（/admin/）
**Django原生管理系统**
- 用户管理：增删改查用户、权限分配
- 数据管理：维护数据集、审核上传数据  
- 下载记录：用户下载历史追踪
- 系统监控：访问日志、错误报告
- 多级权限：超级管理员、普通管理员、审核员等
- **权限分配**：支持多级管理员和普通用户权限。
- **安全性**：仅限授权用户访问。

### 其他页面
- **用户状态页**：展示当前用户的登录状态、基本信息、认证情况。
- **模型介绍页**：介绍平台使用的环境数据模型、算法原理、数据处理流程。
- **论文成果页**：展示平台相关的科研论文、成果发布，支持下载PDF。
- **用户服务页**：FAQ、帮助文档、联系方式、意见反馈等用户支持内容。

