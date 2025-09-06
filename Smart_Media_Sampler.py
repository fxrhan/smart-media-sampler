import os
import random
import shutil
import json
import pickle
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import argparse
import sys
import time
from collections import defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class MediaFileSelector:
    def undo_last_operation(self, destination_folder):
        """Undo the last copy operation by deleting copied files listed in the log file."""
        log_file = Path(destination_folder) / 'selection_log.json'
        if not log_file.exists():
            print(f"❌ No log file found in {destination_folder}. Cannot undo.")
            return False
        try:
            with open(log_file, 'r') as f:
                log_data = json.load(f)
            files = log_data.get('files', [])
            deleted = 0
            for file_path in files:
                dest_file = Path(file_path)
                if dest_file.exists():
                    try:
                        dest_file.unlink()
                        deleted += 1
                    except Exception as e:
                        print(f"⚠️  Could not delete {dest_file}: {e}")
            print(f"↩️  Undo complete. Deleted {deleted} files listed in log.")
            # Optionally, remove the log file after undo
            try:
                log_file.unlink()
            except Exception:
                pass
            return True
        except Exception as e:
            print(f"❌ Failed to undo operation: {e}")
            return False
    def __init__(self):
        self.media_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.bmp', '.tiff', '.webp',
            '.mov', '.avi', '.mkv', '.webm', '.m4v', '.flv',  # More video formats
            '.svg', '.ico', '.heic', '.heif'  # More image formats
        }
        self.operation_state = {}
        self.resume_file = None
        
    def collect_media_files_optimized(self, folder_path, filters=None, use_cache=True):
        """Optimized file collection with caching and filtering"""
        cache_file = Path(folder_path) / '.media_cache.pkl'
        folder = Path(folder_path)
        
        if not folder.exists() or not folder.is_dir():
            print(f"⚠️  Warning: Folder '{folder_path}' doesn't exist or is not accessible")
            return []
        
        # Check cache validity
        if use_cache and cache_file.exists():
            try:
                cache_stat = cache_file.stat()
                folder_stat = folder.stat()
                if cache_stat.st_mtime > folder_stat.st_mtime:
                    with open(cache_file, 'rb') as f:
                        cached_files = pickle.load(f)
                        print(f"📦 Using cached data for {folder_path}")
                        return self.apply_filters(cached_files, filters)
            except:
                pass  # Cache read failed, continue with fresh scan
        
        files_data = []
        print(f"📁 Scanning {folder_path}...")
        
        try:
            for file_path in folder.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in self.media_extensions:
                    try:
                        stat = file_path.stat()
                        file_info = {
                            'path': file_path,
                            'size': stat.st_size,
                            'created': datetime.fromtimestamp(stat.st_ctime),
                            'modified': datetime.fromtimestamp(stat.st_mtime),
                            'extension': file_path.suffix.lower()
                        }
                        
                        # Add metadata for images and videos
                        file_info.update(self.get_media_metadata(file_path))
                        files_data.append(file_info)
                        
                    except (OSError, PermissionError) as e:
                        print(f"⚠️  Couldn't access {file_path}: {e}")
                        continue
        except Exception as e:
            print(f"❌ Error scanning folder {folder_path}: {e}")
            return []
        
        # Cache the results
        if use_cache:
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(files_data, f)
            except:
                pass  # Cache write failed, not critical
        
        return self.apply_filters(files_data, filters)
    
    def get_media_metadata(self, file_path):
        """Extract basic metadata from media files"""
        metadata = {}
        try:
            # For now, just basic info - can be extended with PIL/ffprobe
            if file_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}:
                metadata['type'] = 'image'
                # Could add PIL here for dimensions: width, height
            elif file_path.suffix.lower() in {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.flv'}:
                metadata['type'] = 'video'
                # Could add ffprobe here for duration, resolution
            else:
                metadata['type'] = 'other'
        except:
            metadata['type'] = 'unknown'
        
        return metadata
    
    def apply_filters(self, files_data, filters):
        """Apply various filters to file list"""
        if not filters:
            return files_data
        
        filtered_files = files_data[:]
        
        # Size filters
        if 'min_size' in filters and filters['min_size']:
            min_bytes = self.parse_size(filters['min_size'])
            filtered_files = [f for f in filtered_files if f['size'] >= min_bytes]
        
        if 'max_size' in filters and filters['max_size']:
            max_bytes = self.parse_size(filters['max_size'])
            filtered_files = [f for f in filtered_files if f['size'] <= max_bytes]
        
        # Date filters
        if 'date_from' in filters and filters['date_from']:
            from_date = datetime.strptime(filters['date_from'], '%Y-%m-%d')
            filtered_files = [f for f in filtered_files if f['modified'] >= from_date]
        
        if 'date_to' in filters and filters['date_to']:
            to_date = datetime.strptime(filters['date_to'], '%Y-%m-%d')
            filtered_files = [f for f in filtered_files if f['modified'] <= to_date]
        
        # File type filters
        if 'file_types' in filters and filters['file_types']:
            allowed_types = set(filters['file_types'])
            filtered_files = [f for f in filtered_files if f['extension'] in allowed_types]
        
        # Media type filters
        if 'media_types' in filters and filters['media_types']:
            allowed_media = set(filters['media_types'])
            filtered_files = [f for f in filtered_files if f.get('type') in allowed_media]
        
        return filtered_files
    
    def parse_size(self, size_str):
        """Parse size string like '10MB', '1.5GB' to bytes"""
        size_str = size_str.upper().strip()
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024**2,
            'GB': 1024**3,
            'TB': 1024**4
        }
        
        for suffix, multiplier in multipliers.items():
            if size_str.endswith(suffix):
                try:
                    number = float(size_str[:-len(suffix)])
                    return int(number * multiplier)
                except ValueError:
                    break
        
        try:
            return int(size_str)  # Assume bytes if no suffix
        except ValueError:
            print(f"⚠️  Invalid size format: {size_str}")
            return 0
    
    def get_file_stats(self, files_list):
        """Get statistics about file types and sizes - optimized version"""
        stats = {'types': {}, 'total_size': 0, 'count': len(files_list)}
        
        for file_data in files_list:
            if isinstance(file_data, dict):
                ext = file_data['extension']
                size = file_data['size']
            else:
                # Backward compatibility with old format
                ext = file_data.suffix.lower()
                try:
                    size = file_data.stat().st_size
                except:
                    size = 0
            
            stats['types'][ext] = stats['types'].get(ext, 0) + 1
            stats['total_size'] += size
        
        return stats
    
    def format_size(self, size_bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def save_operation_state(self, state, resume_file):
        """Save operation state for resuming"""
        try:
            with open(resume_file, 'w') as f:
                # Convert Path objects to strings for JSON serialization
                json_state = {}
                for key, value in state.items():
                    if key == 'selected_files':
                        json_state[key] = [str(f['path']) if isinstance(f, dict) else str(f) for f in value]
                    elif key == 'copied_files':
                        json_state[key] = [str(f) for f in value]
                    else:
                        json_state[key] = value
                
                json.dump(json_state, f, indent=2, default=str)
            print(f"💾 Operation state saved to {resume_file}")
        except Exception as e:
            print(f"⚠️  Couldn't save operation state: {e}")
    
    def load_operation_state(self, resume_file):
        """Load operation state for resuming"""
        try:
            with open(resume_file, 'r') as f:
                state = json.load(f)
                # Convert string paths back to Path objects
                if 'selected_files' in state:
                    state['selected_files'] = [Path(f) for f in state['selected_files']]
                if 'copied_files' in state:
                    state['copied_files'] = [Path(f) for f in state['copied_files']]
                return state
        except Exception as e:
            print(f"⚠️  Couldn't load operation state: {e}")
            return None
    
    def select_by_total_size(self, files_data, target_size_str, balanced=False):
        """Select files to reach approximately target total size"""
        target_bytes = self.parse_size(target_size_str)
        
        if balanced:
            # Group files by source folder
            folder_groups = defaultdict(list)
            for file_data in files_data:
                folder_path = file_data['path'].parent
                folder_groups[folder_path].append(file_data)
            
            selected_files = []
            size_per_folder = target_bytes // len(folder_groups)
            
            for folder, files in folder_groups.items():
                folder_size = 0
                folder_files = sorted(files, key=lambda x: x['size'])
                
                for file_data in folder_files:
                    if folder_size + file_data['size'] <= size_per_folder:
                        selected_files.append(file_data)
                        folder_size += file_data['size']
                    if folder_size >= size_per_folder:
                        break
        else:
            # Simple greedy selection
            selected_files = []
            total_size = 0
            shuffled_files = files_data[:]
            random.shuffle(shuffled_files)
            
            for file_data in shuffled_files:
                if total_size + file_data['size'] <= target_bytes:
                    selected_files.append(file_data)
                    total_size += file_data['size']
                if total_size >= target_bytes:
                    break
        
        return selected_files
    
    def copy_files_parallel(self, selected_files, destination_folder, preserve_structure=False, 
                          max_workers=4, resume_file=None):
        """Copy files with parallel processing and resume capability"""
        dest_path = Path(destination_folder)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Load resume state if available
        copied_files = set()
        if resume_file and Path(resume_file).exists():
            state = self.load_operation_state(resume_file)
            if state:
                copied_files = set(state.get('copied_files', []))
                print(f"📁 Resuming operation... {len(copied_files)} files already copied")
        
        # Filter out already copied files
        remaining_files = []
        for file_data in selected_files:
            file_path = file_data['path'] if isinstance(file_data, dict) else file_data
            dest_file = self.get_destination_path(file_path, dest_path, preserve_structure, selected_files)
            if dest_file not in copied_files and not dest_file.exists():
                remaining_files.append(file_data)
        
        if not remaining_files:
            print("✅ All files already copied!")
            return len(selected_files), []
        
        print(f"📋 Copying {len(remaining_files)} files with {max_workers} parallel workers...")
        
        copied_count = len(copied_files)
        errors = []
        
        def copy_single_file(file_data):
            try:
                file_path = file_data['path'] if isinstance(file_data, dict) else file_data
                dest_file = self.get_destination_path(file_path, dest_path, preserve_structure, selected_files)
                
                # Create parent directory if needed
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Handle filename conflicts
                counter = 1
                original_dest = dest_file
                while dest_file.exists():
                    stem = original_dest.stem
                    suffix = original_dest.suffix
                    dest_file = original_dest.parent / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                shutil.copy2(file_path, dest_file)
                return dest_file, None
                
            except Exception as e:
                return None, f"Error copying {file_path}: {e}"
        
        # Use ThreadPoolExecutor for parallel copying
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(copy_single_file, file_data): file_data 
                             for file_data in remaining_files}
            
            for i, future in enumerate(as_completed(future_to_file), 1):
                dest_file, error = future.result()
                
                if error:
                    errors.append(error)
                    print(f"❌ {error}")
                else:
                    copied_files.add(dest_file)
                    copied_count += 1
                
                # Show progress and save state periodically
                if i % 10 == 0 or i == len(remaining_files):
                    print(f"  Progress: {copied_count}/{len(selected_files)} files copied...")
                    
                    # Save resume state
                    if resume_file:
                        state = {
                            'operation': 'copy_files',
                            'total_files': len(selected_files),
                            'copied_files': list(copied_files),
                            'timestamp': datetime.now().isoformat()
                        }
                        self.save_operation_state(state, resume_file)
        
        return copied_count, errors
    
    def get_destination_path(self, file_path, dest_path, preserve_structure, all_selected_files):
        """Get destination path for a file"""
        if preserve_structure:
            # Find source folder for this file
            source_folder = None
            for file_data in all_selected_files:
                f_path = file_data['path'] if isinstance(file_data, dict) else file_data
                if f_path == file_path:
                    # Get the immediate parent folder name
                    source_folder = f_path.parent.name
                    break
            
            if source_folder:
                dest_subfolder = dest_path / source_folder
                dest_subfolder.mkdir(exist_ok=True)
                return dest_subfolder / file_path.name
        
        return dest_path / file_path.name
    
    def save_selection_log(self, selected_files, destination_folder, stats, filters=None):
        """Save a log of which files were selected"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'destination': str(destination_folder),
            'total_selected': len(selected_files),
            'files': [str(f['path']) if isinstance(f, dict) else str(f) for f in selected_files],
            'stats': stats,
            'filters_applied': filters or {}
        }
        
        log_file = Path(destination_folder) / 'selection_log.json'
        try:
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2, default=str)
            print(f"📝 Selection log saved to: {log_file}")
        except Exception as e:
            print(f"⚠️  Couldn't save log file: {e}")
    
    def get_user_input(self, prompt, default=None):
        """Get user input with optional default value"""
        if default:
            user_input = input(f"{prompt} (default: {default}): ").strip()
            return user_input if user_input else str(default)
        else:
            return input(f"{prompt}: ").strip()
    
    def get_filters_interactive(self):
        """Interactive filter configuration"""
        filters = {}
        
        print("\n🔍 File Filtering Options")
        print("=" * 30)
        print("Leave blank to skip any filter")
        
        # Size filters
        min_size = self.get_user_input("Minimum file size (e.g., 1MB, 500KB)").strip()
        if min_size:
            filters['min_size'] = min_size
        
        max_size = self.get_user_input("Maximum file size (e.g., 100MB, 2GB)").strip()
        if max_size:
            filters['max_size'] = max_size
        
        # Date filters
        date_from = self.get_user_input("Files modified from date (YYYY-MM-DD)").strip()
        if date_from:
            try:
                datetime.strptime(date_from, '%Y-%m-%d')
                filters['date_from'] = date_from
            except ValueError:
                print("Invalid date format, skipping date filter")
        
        date_to = self.get_user_input("Files modified to date (YYYY-MM-DD)").strip()
        if date_to:
            try:
                datetime.strptime(date_to, '%Y-%m-%d')
                filters['date_to'] = date_to
            except ValueError:
                print("Invalid date format, skipping date filter")
        
        # File type filters
        file_types = self.get_user_input("File extensions (comma-separated, e.g., .jpg,.png,.mp4)").strip()
        if file_types:
            filters['file_types'] = [ext.strip() for ext in file_types.split(',')]
        
        # Media type filters
        media_types = self.get_user_input("Media types (image,video,other - comma-separated)").strip()
        if media_types:
            filters['media_types'] = [mtype.strip() for mtype in media_types.split(',')]
        
        return filters if filters else None
    
    def select_folders_interactive(self):
        """Interactive folder selection"""
        print("\n📁 Folder Selection")
        print("=" * 30)
        
        source_folders = []
        
        # Get source folders
        print("Enter source folder paths (one per line).")
        print("Press Enter twice when done, or type 'done' to finish:")
        
        while True:
            folder_input = input(f"Source folder {len(source_folders) + 1}: ").strip()
            
            if not folder_input or folder_input.lower() == 'done':
                break
                
            folder_path = Path(folder_input)
            if folder_path.exists() and folder_path.is_dir():
                source_folders.append(str(folder_path))
                print(f"✅ Added: {folder_path}")
            else:
                print(f"❌ Invalid folder: {folder_path}")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    continue
        
        if not source_folders:
            print("❌ No valid source folders provided!")
            return None, None
        
        # Get destination folder
        while True:
            dest_input = self.get_user_input("\nDestination folder path")
            dest_path = Path(dest_input)
            
            # Create destination if it doesn't exist
            if not dest_path.exists():
                create = input(f"Destination '{dest_path}' doesn't exist. Create it? (y/n): ").strip().lower()
                if create == 'y':
                    try:
                        dest_path.mkdir(parents=True, exist_ok=True)
                        print(f"✅ Created destination folder: {dest_path}")
                        break
                    except Exception as e:
                        print(f"❌ Couldn't create folder: {e}")
                        continue
                else:
                    continue
            elif dest_path.is_dir():
                break
            else:
                print(f"❌ '{dest_path}' exists but is not a directory!")
        
        return source_folders, str(dest_path)
    
    def randomly_select_and_copy_files(self, source_folders, destination_folder, num_files=100, 
                                     target_size=None, balanced=False, dry_run=False, 
                                     preserve_structure=False, filters=None, resume_file=None,
                                     max_workers=4, use_cache=True):
        """
        Enhanced file selection and copying with all new features
        """
        
        dest_path = Path(destination_folder)
        if not dest_path.exists() and not dry_run:
            try:
                dest_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created destination folder: {dest_path}")
            except Exception as e:
                print(f"❌ Couldn't create destination folder: {e}")
                return 0
        
        # Setup resume file
        if resume_file is None:
            resume_file = dest_path / 'operation_resume.json'
        
        # Collect all files from all source folders with optimizations
        all_files_data = []
        folder_files = {}
        
        print("📁 Scanning folders with optimizations...")
        start_time = time.time()
        
        # Use parallel scanning for multiple folders
        if len(source_folders) > 1:
            with ThreadPoolExecutor(max_workers=min(len(source_folders), 4)) as executor:
                future_to_folder = {
                    executor.submit(self.collect_media_files_optimized, folder, filters, use_cache): folder 
                    for folder in source_folders
                }
                
                for future in as_completed(future_to_folder):
                    folder = future_to_folder[future]
                    try:
                        files = future.result()
                        folder_files[folder] = files
                        all_files_data.extend(files)
                    except Exception as e:
                        print(f"❌ Error scanning {folder}: {e}")
        else:
            for folder in source_folders:
                files = self.collect_media_files_optimized(folder, filters, use_cache)
                folder_files[folder] = files
                all_files_data.extend(files)
        
        scan_time = time.time() - start_time
        print(f"⏱️  Scanning completed in {scan_time:.2f} seconds")
        
        # Display folder statistics
        for i, folder in enumerate(source_folders, 1):
            files = folder_files[folder]
            stats = self.get_file_stats(files)
            print(f"  Folder {i}: {len(files)} files ({self.format_size(stats['total_size'])})")
            if stats['types']:
                type_summary = ', '.join([f"{ext}: {count}" for ext, count in sorted(stats['types'].items())])
                print(f"    Types: {type_summary}")
        
        print(f"\n📊 Total files found: {len(all_files_data)}")
        if len(all_files_data) == 0:
            print("❌ No media files found matching your criteria!")
            return 0
        
        total_stats = self.get_file_stats(all_files_data)
        print(f"📊 Total size: {self.format_size(total_stats['total_size'])}")
        
        # Selection logic
        if target_size:
            print(f"🎯 Selecting files to reach approximately {target_size}")
            selected_files = self.select_by_total_size(all_files_data, target_size, balanced)
        else:
            if len(all_files_data) < num_files:
                print(f"⚠️  Only {len(all_files_data)} files available, but {num_files} requested.")
                num_files = len(all_files_data)
            
            # Select files based on strategy
            if balanced and len(source_folders) > 0:
                print(f"⚖️  Using balanced selection (approximately {num_files // len(source_folders)} per folder)")
                selected_files = []
                files_per_folder = num_files // len(source_folders)
                remaining = num_files % len(source_folders)
                
                for folder, files in folder_files.items():
                    if files:
                        take = min(files_per_folder + (1 if remaining > 0 else 0), len(files))
                        selected_files.extend(random.sample(files, take))
                        if remaining > 0:
                            remaining -= 1
                
                # If we still need more files, randomly select from remaining
                if len(selected_files) < num_files:
                    remaining_files = [f for f in all_files_data if f not in selected_files]
                    if remaining_files:
                        additional = random.sample(remaining_files, min(num_files - len(selected_files), len(remaining_files)))
                        selected_files.extend(additional)
            else:
                print("🎲 Using completely random selection")
                selected_files = random.sample(all_files_data, num_files)
        
        print(f"\n🎯 Selected {len(selected_files)} files")
        
        # Calculate selection statistics
        selection_stats = self.get_file_stats(selected_files)
        
        if dry_run:
            print("\n🔍 DRY RUN - No files will be copied")
            print(f"Would copy {self.format_size(selection_stats['total_size'])} of data")
            print(f"File type breakdown:")
            for ext, count in sorted(selection_stats['types'].items()):
                print(f"  {ext}: {count} files")
            
            print("\nSample of selected files:")
            for i, file_data in enumerate(selected_files[:10]):
                file_path = file_data['path'] if isinstance(file_data, dict) else file_data
                size = self.format_size(file_data['size']) if isinstance(file_data, dict) else "unknown size"
                print(f"  {i+1}. {file_path} ({size})")
            if len(selected_files) > 10:
                print(f"  ... and {len(selected_files) - 10} more files")
            return len(selected_files)
        
        # Copy selected files with parallel processing and resume capability
        print(f"\n📋 Copying files to {destination_folder}...")
        start_time = time.time()
        
        copied_count, errors = self.copy_files_parallel(
            selected_files, destination_folder, preserve_structure, 
            max_workers, resume_file
        )
        
        copy_time = time.time() - start_time
        print(f"⏱️  Copying completed in {copy_time:.2f} seconds")
        
        # Save selection log
        self.save_selection_log(selected_files, destination_folder, selection_stats, filters)
        
        print(f"\n✅ Successfully copied {copied_count} files to {destination_folder}")
        print(f"📊 Total size copied: {self.format_size(selection_stats['total_size'])}")
        
        if errors:
            print(f"\n⚠️  {len(errors)} errors occurred:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"  • {error}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more errors")
        
        # Clean up resume file on success
        if resume_file and Path(resume_file).exists() and not errors:
            try:
                Path(resume_file).unlink()
                print("🧹 Cleaned up resume file")
            except:
                pass
        
        return copied_count

def parse_folder_list(folder_string):
    """Parse comma-separated folder list"""
    folders = []
    for folder in folder_string.split(','):
        folder = folder.strip()
        if folder:
            folder_path = Path(folder)
            if folder_path.exists() and folder_path.is_dir():
                folders.append(str(folder_path))
            else:
                print(f"⚠️  Warning: Skipping invalid folder: {folder}")
    return folders

def main():
    """Main function with enhanced command line arguments and interactive mode"""
    parser = argparse.ArgumentParser(description='Enhanced Random Media File Selector with advanced filtering and performance optimizations')

    # Basic arguments
    parser.add_argument('--source-folders', '-s', type=str, 
                       help='Comma-separated list of source folder paths')
    parser.add_argument('--destination', '-dest', type=str,
                       help='Destination folder path')
    parser.add_argument('--num-files', '-n', type=int, default=100, 
                       help='Number of files to select (default: 100)')
    parser.add_argument('--target-size', '-size', type=str,
                       help='Target total size instead of file count (e.g., 1GB, 500MB)')

    # Selection options
    parser.add_argument('--balanced', '-b', action='store_true',
                       help='Select equal numbers from each source folder')
    parser.add_argument('--dry-run', '-d', action='store_true',
                       help='Preview what would be copied without actually copying')
    parser.add_argument('--preserve-structure', '-p', action='store_true',
                       help='Maintain source folder structure in destination')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')

    # Filter arguments
    parser.add_argument('--min-size', type=str, help='Minimum file size (e.g., 1MB)')
    parser.add_argument('--max-size', type=str, help='Maximum file size (e.g., 100MB)')
    parser.add_argument('--date-from', type=str, help='Files modified from date (YYYY-MM-DD)')
    parser.add_argument('--date-to', type=str, help='Files modified to date (YYYY-MM-DD)')
    parser.add_argument('--file-types', type=str, help='File extensions (comma-separated)')
    parser.add_argument('--media-types', type=str, help='Media types (image,video,other)')

    # Performance options
    parser.add_argument('--max-workers', type=int, default=4,
                       help='Maximum parallel workers for copying (default: 4)')
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable file scanning cache')
    parser.add_argument('--resume-file', type=str,
                       help='Resume file path for interrupted operations')

    # Undo option (must be here, before parse_args)
    parser.add_argument('--undo', action='store_true', help='Undo the last copy operation (delete copied files)')

    args = parser.parse_args()
    
    # Create selector instance
    selector = MediaFileSelector()
    
    print("🎲 Enhanced Random Media File Selector")
    print("=" * 50)
    
    # Undo functionality (CLI or interactive)
    if args.undo:
        dest = args.destination
        if not dest:
            dest = input("Enter the destination folder to undo last operation: ").strip()
        if not dest:
            print("❌ Destination folder required for undo.")
            return
        selector.undo_last_operation(dest)
        return

    # Determine mode: command line args vs interactive
    if args.interactive or (not args.source_folders and not args.destination):
        print("🔧 Running in interactive mode...")
        source_folders, destination_folder = selector.select_folders_interactive()
        
        if not source_folders:
            print("❌ No source folders provided. Exiting.")
            return

        # Offer undo option interactively
        undo_choice = input("\nDo you want to undo the last operation in the destination folder? (y/n): ").strip().lower()
        if undo_choice == 'y':
            selector.undo_last_operation(destination_folder)
            return

        # Get filters interactively
        use_filters = input("\nDo you want to apply file filters (size, date, type)? (y/n): ").strip().lower() == 'y'
        filters = selector.get_filters_interactive() if use_filters else None

        # Get selection method
        selection_method = input("\nSelection method - (1) by file count or (2) by total size? Enter 1 or 2: ").strip()

        if selection_method == '2':
            target_size = selector.get_user_input("Target total size (e.g., 1GB, 500MB)")
            num_files = None
        else:
            try:
                num_files = int(selector.get_user_input("Number of files to select", args.num_files))
            except ValueError:
                num_files = args.num_files
                print(f"Invalid input, using default: {num_files}")
            target_size = None

        # Get other parameters interactively
        print("\nAdvanced Options:")
        balanced = input("Use balanced selection (select equal numbers from each source folder)? (y/n): ").strip().lower() == 'y'
        dry_run = input("Dry run mode (preview what would be copied without actually copying)? (y/n): ").strip().lower() == 'y'
        preserve_structure = input("Preserve folder structure (keep original folder names in destination)? (y/n): ").strip().lower() == 'y'

        # Performance options
        try:
            max_workers = int(selector.get_user_input("Number of parallel workers for copying", args.max_workers))
        except ValueError:
            max_workers = args.max_workers

        use_cache = input("Use file scanning cache for faster repeated operations? (y/n): ").strip().lower() != 'n'
        
    else:
        # Command line mode
        if not args.source_folders or not args.destination:
            print("❌ Error: Both --source-folders and --destination are required in command line mode")
            print("Use --interactive or -i for interactive mode")
            sys.exit(1)

        source_folders = parse_folder_list(args.source_folders)
        destination_folder = args.destination
        # Ensure destination folder exists or create it
        dest_path = Path(destination_folder)
        if not dest_path.exists():
            try:
                dest_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created destination folder: {dest_path}")
            except Exception as e:
                print(f"❌ Couldn't create destination folder: {e}")
                sys.exit(1)

        num_files = args.num_files if not args.target_size else None
        target_size = args.target_size
        balanced = args.balanced
        dry_run = args.dry_run
        preserve_structure = args.preserve_structure
        max_workers = args.max_workers
        use_cache = not args.no_cache

        # Build filters from command line arguments
        filters = {}
        if args.min_size:
            filters['min_size'] = args.min_size
        if args.max_size:
            filters['max_size'] = args.max_size
        if args.date_from:
            filters['date_from'] = args.date_from
        if args.date_to:
            filters['date_to'] = args.date_to
        if args.file_types:
            filters['file_types'] = [ext.strip() for ext in args.file_types.split(',')]
        if args.media_types:
            filters['media_types'] = [mtype.strip() for mtype in args.media_types.split(',')]

        filters = filters if filters else None

        if not source_folders:
            print("❌ No valid source folders found!")
            sys.exit(1)
    
    # Display configuration
    print(f"\n📂 Source folders: {len(source_folders)} folders")
    for i, folder in enumerate(source_folders, 1):
        print(f"  {i}. {folder}")
    print(f"📁 Destination: {destination_folder}")
    
    if target_size:
        print(f"🎯 Target size: {target_size}")
    else:
        print(f"🎯 Files to select: {num_files}")
    
    if balanced:
        print("⚖️  Mode: Balanced selection")
    if dry_run:
        print("🔍 Mode: Dry run (no files will be copied)")
    if preserve_structure:
        print("📁 Mode: Preserve folder structure")
    
    # Display active filters
    if filters:
        print("\n🔍 Active Filters:")
        if 'min_size' in filters:
            print(f"  📏 Min size: {filters['min_size']}")
        if 'max_size' in filters:
            print(f"  📏 Max size: {filters['max_size']}")
        if 'date_from' in filters:
            print(f"  📅 From date: {filters['date_from']}")
        if 'date_to' in filters:
            print(f"  📅 To date: {filters['date_to']}")
        if 'file_types' in filters:
            print(f"  📄 File types: {', '.join(filters['file_types'])}")
        if 'media_types' in filters:
            print(f"  🎬 Media types: {', '.join(filters['media_types'])}")
    
    print(f"⚡ Performance: {max_workers} parallel workers, caching {'enabled' if use_cache else 'disabled'}")
    print("-" * 50)
    
    # Confirm before proceeding (unless dry run)
    if not dry_run:
        print("\n⚠️  This will copy files to your destination folder.")
        confirm = input("Proceed with file copying? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled.")
            return
    
    try:
        copied = selector.randomly_select_and_copy_files(
            source_folders=source_folders,
            destination_folder=destination_folder,
            num_files=num_files,
            target_size=target_size,
            balanced=balanced,
            dry_run=dry_run,
            preserve_structure=preserve_structure,
            filters=filters,
            resume_file=args.resume_file,
            max_workers=max_workers,
            use_cache=use_cache
        )
        
        if not dry_run and copied > 0:
            print(f"\n🎉 Process completed! {copied} files randomly selected and copied.")
            print("💡 Tip: Use --resume-file to resume if operation is interrupted next time")
        elif dry_run:
            print(f"\n🔍 Dry run completed! Would have copied {copied} files.")
        else:
            print("\n❌ No files were copied. Please check your folder paths and permissions.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user.")
        print("💡 You can resume this operation later using the resume file in the destination folder")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("Please check that your folder paths are correct and accessible.")
        print("💡 If operation was interrupted, you can resume using --resume-file")

# Main execution
if __name__ == "__main__":
    main()