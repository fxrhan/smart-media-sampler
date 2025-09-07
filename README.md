# 🎲 Smart Media Sampler

A professional-grade Python tool for intelligently selecting and copying media files from multiple source directories with advanced filtering, performance optimizations, and resume capabilities. Perfect for creating datasets, content curation, quality assurance, and large-scale media management.

## ✨ Key Features

- 🎯 **Smart Selection**: Choose by file count OR total size
- ⚖️ **Balanced Sampling**: Equal distribution across source folders
- 🔍 **Advanced Filtering**: Size, date, type, and metadata filters
- ⚡ **High Performance**: Parallel processing and intelligent caching
- 🔄 **Resume Capability**: Never lose progress on interrupted operations
- 📊 **Detailed Analytics**: Comprehensive statistics and reporting
- 🛡️ **Robust Error Handling**: Graceful failure recovery
- 🚀 **Interactive Mode**: User-friendly guided setup

## 📋 Supported File Types

### Images
- `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`
- `.svg`, `.ico`, `.heic`, `.heif`

### Videos
- `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.m4v`, `.flv`

## 🔧 Installation & Setup

### Prerequisites
- **Python 3.6+** (Required)
- **No external dependencies** (uses only standard library)

### Quick Setup
1. Download `enhanced_media_selector.py`
2. Make executable (optional):
   ```bash
   chmod +x enhanced_media_selector.py
   ```
3. Test installation:
   ```bash
   python enhanced_media_selector.py --help
   ```

## 🚀 Quick Start Guide

### 1. Interactive Mode (Recommended for Beginners)
```bash
python enhanced_media_selector.py --interactive
```
Follow the guided prompts to:
- Select source folders
- Choose destination
- Configure filters
- Set selection criteria

### 2. Simple Command Line Usage
```bash
# Basic selection: 100 random files
python enhanced_media_selector.py \
  -s "/home/photos,/home/videos" \
  -dest "/home/selection" \
  -n 100

# Size-based selection: 2GB of files
python enhanced_media_selector.py \
  -s "/media/collection" \
  -dest "/output" \
  --target-size 2GB
```

## 📖 Comprehensive Usage Guide

### Selection Methods

#### **Method 1: By File Count**
Select a specific number of files:
```bash
python enhanced_media_selector.py \
  -s "/photos,/videos" \
  -dest "/sample" \
  -n 500 \
  --balanced
```

#### **Method 2: By Total Size**
Select files to reach a target total size:
```bash
python enhanced_media_selector.py \
  -s "/media" \
  -dest "/size_sample" \
  --target-size 1.5GB \
  --balanced
```

### Advanced Filtering

#### **Size Filtering**
```bash
# Only files between 1MB and 50MB
python enhanced_media_selector.py \
  -s "/collection" -dest "/filtered" -n 200 \
  --min-size 1MB --max-size 50MB
```

#### **Date Filtering**
```bash
# Only files modified in 2024
python enhanced_media_selector.py \
  -s "/archive" -dest "/recent" -n 100 \
  --date-from 2024-01-01 --date-to 2024-12-31
```

#### **File Type Filtering**
```bash
# Only JPEG images and MP4 videos
python enhanced_media_selector.py \
  -s "/mixed_media" -dest "/specific" -n 150 \
  --file-types .jpg,.jpeg,.mp4
```

#### **Media Type Filtering**
```bash
# Only images (no videos)
python enhanced_media_selector.py \
  -s "/everything" -dest "/images_only" -n 300 \
  --media-types image
```

### Performance Optimization

#### **High-Performance Setup**
```bash
# Maximum performance for large collections
python enhanced_media_selector.py \
  -s "/massive/collection" -dest "/output" -n 1000 \
  --max-workers 8 \
  --preserve-structure
```

#### **Cache Management**
```bash
# Disable cache for one-time operations
python enhanced_media_selector.py \
  -s "/temp/folder" -dest "/output" -n 50 \
  --no-cache

# Use cache for repeated operations (default)
python enhanced_media_selector.py \
  -s "/regular/source" -dest "/output" -n 100
```

### Resume Interrupted Operations

#### **Automatic Resume**
If an operation is interrupted, simply re-run the same command:
```bash
# This will automatically resume if interrupted
python enhanced_media_selector.py \
  -s "/large/collection" -dest "/output" -n 2000
```

#### **Custom Resume File**
```bash
# Specify custom resume file location
python enhanced_media_selector.py \
  -s "/source" -dest "/dest" -n 500 \
  --resume-file "/backup/my_operation.json"
```

## 🎛️ Complete Command Reference

### Basic Options
| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--source-folders` | `-s` | Source folder paths (comma-separated) | `-s "/photos,/videos"` |
| `--destination` | `-dest` | Destination folder path | `-dest "/output"` |
| `--interactive` | `-i` | Run interactive mode | `-i` |

### Selection Options
| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--num-files` | `-n` | Number of files to select | `-n 500` |
| `--target-size` | `-size` | Target total size | `--target-size 2GB` |
| `--balanced` | `-b` | Equal selection from each folder | `-b` |
| `--preserve-structure` | `-p` | Keep folder hierarchy | `-p` |
| `--dry-run` | `-d` | Preview without copying | `-d` |

### Filter Options
| Option | Description | Example |
|--------|-------------|---------|
| `--min-size` | Minimum file size | `--min-size 1MB` |
| `--max-size` | Maximum file size | `--max-size 100MB` |
| `--date-from` | Files modified after date | `--date-from 2024-01-01` |
| `--date-to` | Files modified before date | `--date-to 2024-12-31` |
| `--file-types` | Specific extensions | `--file-types .jpg,.png` |
| `--media-types` | Media categories | `--media-types image,video` |

### Performance Options
| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--max-workers` | Parallel processing threads | 4 | `--max-workers 8` |
| `--no-cache` | Disable file scanning cache | False | `--no-cache` |
| `--resume-file` | Custom resume file path | Auto | `--resume-file /path/file.json` |

## 💼 Real-World Use Cases

### 1. Machine Learning Dataset Creation
```bash
# Create balanced training dataset
python enhanced_media_selector.py \
  --interactive
# Select: 10,000 images, balanced, filter by size (>100KB)
```

### 2. Content Quality Assurance
```bash
# Random sample for manual review
python enhanced_media_selector.py \
  -s "/production/uploads" \
  -dest "/qa_review" \
  -n 100 \
  --date-from 2024-11-01 \
  --dry-run
```

### 3. Archive Sampling
```bash
# Create representative archive sample
python enhanced_media_selector.py \
  -s "/archive/2023,/archive/2024" \
  -dest "/sample" \
  --target-size 5GB \
  --balanced \
  --preserve-structure \
  --min-size 500KB
```

### 4. Portfolio Curation
```bash
# Curate diverse portfolio
python enhanced_media_selector.py \
  -s "/work/projects" \
  -dest "/portfolio" \
  -n 200 \
  --media-types image \
  --min-size 2MB \
  --balanced
```

### 5. Backup Verification
```bash
# Random backup sample for verification
python enhanced_media_selector.py \
  -s "/backup/photos" \
  -dest "/verify_sample" \
  --target-size 500MB \
  --max-workers 2
```

## 📊 Understanding Output

### Console Output Example
```
🎲 Enhanced Random Media File Selector
==================================================
📁 Scanning folders with optimizations...
📦 Using cached data for /home/photos
  Folder 1: 2,450 files (4.2 GB)
    Types: .jpg: 1800, .png: 450, .gif: 200
  Folder 2: 1,200 files (2.8 GB)
    Types: .mp4: 800, .mov: 400

📊 Total files found: 3,650
📊 Total size: 7.0 GB
⏱️  Scanning completed in 0.45 seconds

🔍 Active Filters:
  📏 Min size: 1MB
  📅 From date: 2024-01-01

🎯 Target size: 1GB
⚖️  Using balanced selection

📋 Copying files to /output...
  Progress: 120/120 files copied...
⏱️  Copying completed in 8.32 seconds

✅ Successfully copied 120 files to /output
📊 Total size copied: 1.02 GB
📝 Selection log saved to: /output/selection_log.json
```

### Selection Log Structure
The tool creates detailed JSON logs:
```json
{
  "timestamp": "2024-03-15T14:30:22.123456",
  "destination": "/output/folder",
  "total_selected": 120,
  "files": [
    "/source/image1.jpg",
    "/source/video1.mp4"
  ],
  "stats": {
    "types": {".jpg": 80, ".mp4": 40},
    "total_size": 1073741824,
    "count": 120
  },
  "filters_applied": {
    "min_size": "1MB",
    "date_from": "2024-01-01"
  }
}
```

## ⚡ Performance Guide

### Optimizing for Large Collections

#### **For Collections > 100K Files**
```bash
python enhanced_media_selector.py \
  -s "/massive/archive" \
  -dest "/sample" \
  --target-size 10GB \
  --max-workers 8 \
  --balanced
```

#### **For Network Storage**
```bash
# Reduce workers for network drives
python enhanced_media_selector.py \
  -s "/network/drive" \
  -dest "/local/output" \
  -n 1000 \
  --max-workers 2
```

#### **Memory Optimization**
- Use `--target-size` instead of large `-n` values
- Enable caching for repeated operations
- Use specific filters to reduce dataset size

### Performance Benchmarks
| Collection Size | Scan Time | Copy Time (1000 files) |
|-----------------|-----------|------------------------|
| 10K files | 2-5 seconds | 15-30 seconds |
| 100K files | 15-30 seconds | 2-4 minutes |
| 1M+ files | 1-3 minutes | 5-10 minutes |

*Times vary based on storage type and system specifications*

## 🔧 Advanced Configuration

### Interactive Mode Walkthrough

1. **Folder Selection**
   ```
   📁 Folder Selection
   ==============================
   Enter source folder paths (one per line).
   Press Enter twice when done, or type 'done' to finish:
   Source folder 1: /home/photos
   ✅ Added: /home/photos
   Source folder 2: /media/videos
   ✅ Added: /media/videos
   Source folder 3: done
   
   Destination folder path: /output
   ✅ Created destination folder: /output
   ```

2. **Filter Configuration**
   ```
   Do you want to apply file filters (size, date, type)? (y/n): y
   
   🔍 File Filtering Options
   ==============================
   Leave blank to skip any filter
   Minimum file size (e.g., 1MB, 500KB): 2MB
   Maximum file size (e.g., 100MB, 2GB): 50MB
   Files modified from date (YYYY-MM-DD): 2024-01-01
   Files modified to date (YYYY-MM-DD): 
   File extensions (comma-separated, e.g., .jpg,.png,.mp4): .jpg,.png
   Media types (image,video,other - comma-separated): image
   ```

3. **Selection Configuration**
   ```
   Selection method - (1) by file count or (2) by total size? Enter 1 or 2: 2
   Target total size (e.g., 1GB, 500MB): 2GB
   
   Advanced Options:
   Use balanced selection (select equal numbers from each source folder)? (y/n): y
   Dry run mode (preview what would be copied without actually copying)? (y/n): n
   Preserve folder structure (keep original folder names in destination)? (y/n): y
   Number of parallel workers for copying (default: 4): 6
   Use file scanning cache for faster repeated operations? (y/n): y
   ```

### Automation Scripts

#### **Daily Sampling Script**
```bash
#!/bin/bash
# daily_sample.sh
DATE=$(date +%Y-%m-%d)
python enhanced_media_selector.py \
  -s "/production/uploads" \
  -dest "/qa/samples/$DATE" \
  -n 50 \
  --date-from $DATE \
  --max-workers 4
```

#### **Weekly Archive Script**
```bash
#!/bin/bash
# weekly_archive.sh
WEEK_AGO=$(date -d '7 days ago' +%Y-%m-%d)
python enhanced_media_selector.py \
  -s "/archive/photos,/archive/videos" \
  -dest "/samples/weekly" \
  --target-size 1GB \
  --balanced \
  --date-from $WEEK_AGO \
  --preserve-structure
```

## ⚠️ Important Notes & Best Practices

### File Handling
- **Automatic conflict resolution**: Duplicate names get numbered suffixes
- **Metadata preservation**: File timestamps and permissions are maintained
- **Safe operations**: Original files are never modified or deleted

### Resume Operations
- **Automatic detection**: Detects incomplete operations automatically
- **State persistence**: Operation state saved every 10 files
- **Clean recovery**: Skips already copied files when resuming

### Cache Behavior
- **Location**: Cache stored as `.media_cache.pkl` in each source folder
- **Validity**: Automatically invalidated when folder is modified
- **Size**: Minimal overhead, even for large collections
- **Cleanup**: Can be safely deleted if needed

### Error Handling
- **Graceful degradation**: Continues operation despite individual file errors
- **Detailed reporting**: Specific error messages for each failure
- **Partial success**: Reports successful operations even if some files fail

## 🐛 Troubleshooting

### Common Issues & Solutions

**"No media files found matching your criteria"**
- Check that source folders contain supported file types
- Verify filter criteria aren't too restrictive
- Use `--dry-run` to test filters first

**"Permission denied" errors**
- Ensure read access to source folders
- Ensure write access to destination folder
- On Unix systems: `chmod 755 /path/to/folders`

**Slow performance with large collections**
- Increase `--max-workers` (try 6-8)
- Enable caching for repeated operations
- Use specific filters to reduce dataset size
- Consider using `--target-size` instead of large file counts

**Memory usage issues**
- Use filters to reduce dataset size
- Process in smaller batches
- Enable caching to avoid repeated scans

**Resume not working**
- Check if resume file exists in destination folder
- Verify destination folder hasn't been modified
- Try specifying custom `--resume-file` path

### Performance Troubleshooting

**Scanning is slow**
```bash
# Enable caching and use parallel scanning
python enhanced_media_selector.py -s "/large/folder" -dest "/out" -n 100
# Second run will be much faster
```

**Copying is slow**
```bash
# Increase parallel workers
python enhanced_media_selector.py -s "/source" -dest "/dest" -n 500 --max-workers 8
```

**High memory usage**
```bash
# Use size-based selection instead of large counts
python enhanced_media_selector.py -s "/source" -dest "/dest" --target-size 1GB
```

### Getting Help

1. **Check the help**: `python enhanced_media_selector.py --help`
2. **Use dry-run mode**: Test operations with `--dry-run`
3. **Enable interactive mode**: Use `-i` for guided troubleshooting
4. **Check permissions**: Verify folder access rights
5. **Test with small datasets**: Start small, then scale up

## 🎯 Pro Tips

### Efficiency Tips
- **Use caching**: Let the tool cache folder scans for repeated operations
- **Start with dry-run**: Always test filters and selection with `--dry-run`
- **Optimize workers**: 4-8 workers work best for most systems
- **Size-based selection**: Often more intuitive than count-based

### Quality Tips
- **Use balanced selection**: Ensures representative sampling
- **Apply minimum size filters**: Avoid tiny/corrupted files
- **Filter by date**: Focus on recent or specific time periods
- **Preserve structure**: Maintain organization for easier management

### Workflow Tips
- **Interactive mode first**: Use interactive mode to understand options
- **Save successful commands**: Keep a record of working commands
- **Use resume capability**: Don't worry about interruptions
- **Check logs**: Review selection logs for insights

## 📄 License & Contributing

This tool is provided as-is for educational and professional use. Feel free to modify and distribute according to your needs.
