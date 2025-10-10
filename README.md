# 视频帧序列处理器 (Video Frame Processor)

<div align="center">

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

一个强大的视频帧提取和批处理工具，支持自动裁剪、Photoshop 抠图和批量调整分辨率。

[English](README_EN.md) | 简体中文

</div>

## ✨ 功能特性

- 🎬 **批量视频处理** - 支持同时处理多个视频文件
- 🔪 **智能帧提取** - 可自定义帧间隔，减少冗余帧
- ✂️ **精确裁剪** - 支持自定义裁剪区域和偏移量，实时预览
- 🎨 **Photoshop 集成** - 自动调用 Photoshop 动作进行批量抠图
- 📐 **批量调整大小** - 统一输出分辨率
- 🌍 **多语言支持** - 中文/英文界面切换
- 📊 **实时进度显示** - 详细的日志和进度条
- 🎭 **蒙版预览** - 支持加载蒙版图片进行预览

## 📸 截图

![主界面](screenshot.png)

## 🚀 快速开始

### 方式一：使用打包好的可执行文件（推荐）

1. 从 [Releases](../../releases) 页面下载最新版本的 `main.exe`
2. 下载 `run_action_template.jsx` 文件（必需）
3. 将两个文件放在同一目录下
4. 双击运行 `main.exe`

### 方式二：从源码运行

#### 前置要求

- Python 3.8 或更高版本
- FFmpeg（用于视频帧提取）
- ImageMagick（用于图片处理）
- Adobe Photoshop（可选，用于抠图功能）

#### 安装依赖

```bash
pip install pillow
```

#### 运行程序

```bash
python main.py
```

## 📖 使用说明

### 基本工作流程

1. **添加视频** - 点击"添加视频文件"按钮选择要处理的视频
2. **配置参数** - 设置裁剪区域、帧间隔、输出分辨率等
3. **预览效果** - 选择视频后点击"手动预览"查看裁剪效果
4. **应用设置** - 点击"应用到选中项"将参数应用到选中的视频
5. **开始处理** - 点击"开始处理"按钮开始批量处理

### 处理步骤说明

程序支持四个可选的处理步骤：

1. **减帧** - 按指定间隔提取视频帧（例如每3帧取1帧）
2. **裁剪** - 按指定区域和偏移量裁剪图片
3. **抠图 (PS)** - 调用 Photoshop 动作进行批量抠图
4. **缩放** - 统一调整图片分辨率

### Photoshop 动作设置

如果需要使用 Photoshop 抠图功能：

1. 在 Photoshop 中创建一个名为 `RemoveBackground` 的动作
2. 动作应该包含你的抠图步骤（例如：魔棒选择、删除背景等）
3. 在程序设置中配置 Photoshop 的安装路径

### 输出文件

处理完成后，文件会保存在程序目录下的 `output` 文件夹中：

```
output/
├── 视频名称1/
│   ├── 1_reduced_frames/    # 减帧后的图片
│   ├── 2_cropped_frames/    # 裁剪后的图片
│   ├── 3_transparent_temp/  # 抠图后的图片
│   └── 4_final_output/      # 最终输出
└── 视频名称2/
    └── ...
```

## ⚙️ 配置说明

### 设置文件

程序会在运行目录下创建 `settings.json` 文件保存配置：

```json
{
    "photoshop_exe": "C:\\Program Files\\Adobe\\Adobe Photoshop 2025\\Photoshop.exe",
    "language": "zh",
    "frame_step": "3",
    "final_w": "128",
    "final_h": "128",
    "geometry": "1000x750"
}
```

### 语言文件

- `lang_zh.json` - 中文界面
- `lang_en.json` - 英文界面

## 🛠️ 开发

### 项目结构

```
video-frame-processor/
├── main.py                      # 主程序
├── run_action_template.jsx      # Photoshop 脚本模板
├── lang_zh.json                 # 中文语言包
├── lang_en.json                 # 英文语言包
├── settings.json                # 配置文件（自动生成）
└── output/                      # 输出目录（自动生成）
```

### 打包为可执行文件

```bash
pyinstaller --onefile --windowed --icon=icon.ico --add-data "run_action_template.jsx;." main.py
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 更新日志

### v1.0 (2025-10-10)
- ✨ 添加实时日志和进度显示
- 🐛 修复打包后资源文件路径问题
- ⚡ 优化预览性能，添加缓存机制
- 🔇 隐藏子进程命令行窗口
- 📁 修复输出目录在 exe 旁边生成



## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [FFmpeg](https://ffmpeg.org/) - 视频处理
- [ImageMagick](https://imagemagick.org/) - 图片处理
- [Pillow](https://python-pillow.org/) - Python 图像库

## 💬 联系方式

如有问题或建议，欢迎：
- 提交 [Issue](../../issues)
- 发起 [Discussion](../../discussions)

---

<div align="center">
Made with ❤️ by [Atthepiano]
</div>
