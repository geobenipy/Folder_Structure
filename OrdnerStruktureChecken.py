#!/usr/bin/env python3
"""
Directory Structure Scanner
Recursively scans and displays folder hierarchies with detailed statistics.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# Configuration
TARGET_DIRECTORY = r"E:\Miscellaneous\Skripte&Tutorials\!!!Auf_GIT\Cluttergrams\New_Paper\code\qgis-plugin\Seismic_Scatter"  # Change this to your target directory path
EXCLUDED_DIRECTORIES = [".git", "__pycache__", "node_modules", ".venv", "venv", "Data", "Output", "Results", "doc", ".idea", "obsolete", "pyaid.egg-info", "pyaid-example", "pyaidrl", "pyaidrlbaselines"]  # Directories to skip


class DirectoryScanner:
    def __init__(self, root_path, excluded_dirs):
        self.root = Path(root_path).resolve()
        self.excluded_dirs = set(excluded_dirs)
        self.stats = {
            'total_files': 0,
            'total_dirs': 0,
            'total_size': 0,
            'file_types': defaultdict(int),
            'largest_files': [],
            'skipped_dirs': 0
        }
        
    def get_size(self, path):
        try:
            return path.stat().st_size
        except (OSError, PermissionError):
            return 0
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def scan_directory(self, path, prefix="", is_last=True):
        try:
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            print(f"{prefix}[Permission Denied]")
            return
        
        for idx, entry in enumerate(entries):
            is_final = idx == len(entries) - 1
            connector = "└── " if is_final else "├── "
            extension = "    " if is_final else "│   "
            
            if entry.is_file():
                size = self.get_size(entry)
                self.stats['total_files'] += 1
                self.stats['total_size'] += size
                
                ext = entry.suffix.lower() or 'no_ext'
                self.stats['file_types'][ext] += 1
                
                self.stats['largest_files'].append((entry, size))
                if len(self.stats['largest_files']) > 10:
                    self.stats['largest_files'].sort(key=lambda x: x[1], reverse=True)
                    self.stats['largest_files'] = self.stats['largest_files'][:10]
                
                print(f"{prefix}{connector}{entry.name} ({self.format_size(size)})")
                
            elif entry.is_dir():
                if entry.name in self.excluded_dirs:
                    self.stats['skipped_dirs'] += 1
                    print(f"{prefix}{connector}{entry.name}/ [SKIPPED]")
                    continue
                
                self.stats['total_dirs'] += 1
                print(f"{prefix}{connector}{entry.name}/")
                self.scan_directory(entry, prefix + extension, is_final)
    
    def print_statistics(self):
        print("\n" + "="*70)
        print("SCAN STATISTICS")
        print("="*70)
        print(f"Total Directories: {self.stats['total_dirs']}")
        print(f"Total Files: {self.stats['total_files']}")
        print(f"Total Size: {self.format_size(self.stats['total_size'])}")
        
        if self.stats['skipped_dirs'] > 0:
            print(f"Skipped Directories: {self.stats['skipped_dirs']}")
        
        if self.stats['file_types']:
            print(f"\nFile Type Distribution:")
            sorted_types = sorted(self.stats['file_types'].items(), 
                                key=lambda x: x[1], reverse=True)
            for ext, count in sorted_types[:15]:
                print(f"  {ext:15s} : {count:5d} files")
        
        if self.stats['largest_files']:
            print(f"\nLargest Files:")
            for file_path, size in self.stats['largest_files'][:10]:
                rel_path = file_path.relative_to(self.root)
                print(f"  {self.format_size(size):>12s}  {rel_path}")
        
        print("="*70)
    
    def run(self):
        if not self.root.exists():
            print(f"Error: Path '{self.root}' does not exist.")
            sys.exit(1)
        
        if not self.root.is_dir():
            print(f"Error: Path '{self.root}' is not a directory.")
            sys.exit(1)
        
        print(f"\nScanning: {self.root}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*70)
        print(f"{self.root.name}/")
        
        self.scan_directory(self.root)
        self.print_statistics()


def main():
    scanner = DirectoryScanner(TARGET_DIRECTORY, EXCLUDED_DIRECTORIES)
    scanner.run()


if __name__ == "__main__":
    main()