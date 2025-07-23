# MED环境数据平台 - pip镜像源配置指南

## 快速配置

运行以下脚本来自动配置pip使用国内镜像源：

```bash
# Windows用户
quick_install_django.bat

# 或者
setup_pip_mirrors.bat
```

## 手动配置方法

### 方法1：临时使用镜像源
```bash
# 清华大学镜像源（推荐）
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple Django==4.2.16

# 阿里云镜像源
pip install -i https://mirrors.aliyun.com/pypi/simple/ Django==4.2.16

# 腾讯云镜像源
pip install -i https://mirrors.cloud.tencent.com/pypi/simple/ Django==4.2.16

# 豆瓣镜像源
pip install -i https://pypi.douban.com/simple/ Django==4.2.16

# 华为云镜像源
pip install -i https://mirrors.huaweicloud.com/repository/pypi/simple/ Django==4.2.16
```

### 方法2：永久配置镜像源

#### Windows用户
1. 创建配置目录：
   ```cmd
   mkdir %APPDATA%\pip
   ```

2. 创建配置文件 `%APPDATA%\pip\pip.ini`：
   ```ini
   [global]
   index-url = https://pypi.tuna.tsinghua.edu.cn/simple
   trusted-host = pypi.tuna.tsinghua.edu.cn
   timeout = 120

   [install]
   trusted-host = pypi.tuna.tsinghua.edu.cn
   ```

#### Linux/macOS用户
1. 创建配置目录：
   ```bash
   mkdir -p ~/.pip
   ```

2. 创建配置文件 `~/.pip/pip.conf`：
   ```ini
   [global]
   index-url = https://pypi.tuna.tsinghua.edu.cn/simple
   trusted-host = pypi.tuna.tsinghua.edu.cn
   timeout = 120

   [install]
   trusted-host = pypi.tuna.tsinghua.edu.cn
   ```

## 常用国内镜像源列表

| 镜像源名称 | 地址 |
|-----------|------|
| 清华大学 | https://pypi.tuna.tsinghua.edu.cn/simple |
| 阿里云 | https://mirrors.aliyun.com/pypi/simple/ |
| 腾讯云 | https://mirrors.cloud.tencent.com/pypi/simple/ |
| 豆瓣 | https://pypi.douban.com/simple/ |
| 华为云 | https://mirrors.huaweicloud.com/repository/pypi/simple/ |
| 网易 | https://mirrors.163.com/pypi/simple/ |
| 中科大 | https://pypi.mirrors.ustc.edu.cn/simple/ |

## 验证配置

配置完成后，运行以下命令验证：

```bash
# 查看当前pip配置
pip config list

# 测试安装速度
pip install --upgrade pip

# 安装Django测试
pip install Django==4.2.16
```

## 常见问题

### Q1: 遇到SSL证书错误
```bash
pip install --trusted-host pypi.tuna.tsinghua.edu.cn -i https://pypi.tuna.tsinghua.edu.cn/simple Django==4.2.16
```

### Q2: 超时问题
在pip.ini/pip.conf中添加：
```ini
[global]
timeout = 120
```

### Q3: 清除pip缓存
```bash
pip cache purge
```

## 自动化脚本说明

- `quick_install_django.bat`: 快速安装Django，自动尝试多个镜像源
- `setup_pip_mirrors.bat`: 配置永久镜像源设置
- `start_server.bat`: 启动Django服务器（已集成镜像源支持）

运行任一脚本即可自动配置pip镜像源并安装Django。
