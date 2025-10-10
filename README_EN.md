# Video Frame Processor

<div align="center">

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

A powerful video frame extraction and batch processing tool with support for automatic cropping, Photoshop integration, and batch resizing.

English | [简体中文](README.md)

</div>

## ✨ Features

- 🎬 **Batch Video Processing** - Process multiple video files simultaneously
- 🔪 **Smart Frame Extraction** - Customizable frame intervals to reduce redundancy
- ✂️ **Precise Cropping** - Custom crop areas with offset support and real-time preview
- 🎨 **Photoshop Integration** - Automatic batch processing with Photoshop actions
- 📐 **Batch Resizing** - Unified output resolution
- 🌍 **Multi-language Support** - Chinese/English interface
- 📊 **Real-time Progress** - Detailed logs and progress bars
- 🎭 **Mask Preview** - Load mask images for preview

## 📸 Screenshots

![Main Interface](screenshot.png)

## 🚀 Quick Start

### Option 1: Use Pre-built Executable (Recommended)

1. Download the latest `main.exe` from [Releases](../../releases)
2. Download the `run_action_template.jsx` file (required)
3. Place both files in the same directory
4. Double-click `main.exe` to run

### Option 2: Run from Source

#### Prerequisites

- Python 3.8 or higher
- FFmpeg (for video frame extraction)
- ImageMagick (for image processing)
- Adobe Photoshop (optional, for background removal)

#### Install Dependencies

```bash
pip install pillow
```

#### Run the Program

```bash
python main.py
```

## 📖 Usage Guide

### Basic Workflow

1. **Add Videos** - Click "Add Video" to select videos to process
2. **Configure Parameters** - Set crop area, frame interval, output resolution, etc.
3. **Preview** - Select a video and click "Preview" to see the crop effect
4. **Apply Settings** - Click "Apply to Selected" to apply parameters
5. **Start Processing** - Click "Start Processing" to begin batch processing

### Processing Steps

The program supports four optional processing steps:

1. **Frame Reduction** - Extract frames at specified intervals (e.g., 1 frame per 3)
2. **Cropping** - Crop images to specified area and offset
3. **Background Removal (PS)** - Batch process with Photoshop actions
4. **Resizing** - Resize images to unified resolution

### Photoshop Action Setup

To use the Photoshop background removal feature:

1. Create an action named `RemoveBackground` in Photoshop
2. The action should include your background removal steps
3. Configure Photoshop installation path in program settings

### Output Files

Processed files are saved in the `output` folder:

```
output/
├── video_name1/
│   ├── 1_reduced_frames/    # Frames after reduction
│   ├── 2_cropped_frames/    # Cropped frames
│   ├── 3_transparent_temp/  # After background removal
│   └── 4_final_output/      # Final output
└── video_name2/
    └── ...
```

## ⚙️ Configuration

### Settings File

The program creates a `settings.json` file:

```json
{
    "photoshop_exe": "C:\\Program Files\\Adobe\\Adobe Photoshop 2025\\Photoshop.exe",
    "language": "en",
    "frame_step": "3",
    "final_w": "128",
    "final_h": "128",
    "geometry": "1000x750"
}
```

### Language Files

- `lang_zh.json` - Chinese interface
- `lang_en.json` - English interface

## 🛠️ Development

### Project Structure

```
video-frame-processor/
├── main.py                      # Main program
├── run_action_template.jsx      # Photoshop script template
├── lang_zh.json                 # Chinese language pack
├── lang_en.json                 # English language pack
├── settings.json                # Config file (auto-generated)
└── output/                      # Output directory (auto-generated)
```

### Build Executable

```bash
pyinstaller --onefile --windowed --icon=icon.ico --add-data "run_action_template.jsx;." main.py
```

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📝 Changelog

### v1.0 (2025-10-10)
- ✨ Added real-time logs and progress display
- 🐛 Fixed resource file path issues after packaging
- ⚡ Optimized preview performance with caching
- 🔇 Hidden subprocess console windows
- 📁 Fixed output directory generation next to exe



## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- [FFmpeg](https://ffmpeg.org/) - Video processing
- [ImageMagick](https://imagemagick.org/) - Image processing
- [Pillow](https://python-pillow.org/) - Python imaging library

## 💬 Contact

For questions or suggestions:
- Submit an [Issue](../../issues)
- Start a [Discussion](../../discussions)

---

<div align="center">
Made with ❤️ by [Atthepiano]
</div>
