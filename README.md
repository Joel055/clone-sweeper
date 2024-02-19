# clone-sweeper

clone-sweeper started from a personal frustration with my Clone Hero song library. As a big fan of the game, I've accumulated thousands of songs, only to realize many were duplicates. These weren't just cluttering the folders; they were consuming valuable disk space. Motivated by a sheer reluctance to sift through these folders manually, I started developing clone-sweeper, fittingly named after the game that sparked its creation. This Python-built utility is designed to streamline the identification and management of duplicate files, freeing up disk space and making folders easier on the eyes.
## Features

- **Flexible Scanning**: Users can specify multiple paths or, by default, the current directory where clone-sweeper is executed.
- **Exclusions** Pre-configured exclusions for system and non-essential files to optimize scanning efficiency.
- **Custom Exclusions**: The tool allows for the exclusion of certain paths, file extensions, or filenames to customize the scanning process according to user preferences.
- **Interactive Menu**: Utilizes a custom-built, console-based menu class for straightforward navigation and configuration of settings.
- **Cache Optimization**: Implements smart caching to speed up subsequent scans by bypassing the re-calculation of hashes for unchanged files.
- **Reporting**: Generates a report of identified duplicates, organizing them into groups based on identical hashes, and presents this information in a "duplicates.json" file.
- **Advanced**: Selectable hashing algorithms, chunk sizes, and file size thresholds in "settings.json".

## Getting Started

### Prerequisites

- Python 3.10 or newer
- 'tqdm' library for progress bar functionality.

### Installation

1. Begin by cloning the CloneSweeper repository:

   ```bash
   git clone https://github.com/Joel055/clone-sweeper
2. To install 'tqdm' for progress bar functionality, run:

   ```bash
   pip install tqdm

To run the program go into its root directory and start "main.py":
```bash
python main.py
```

## Roadmap
clone-sweeper is under continuous development with plans to incorporate:

* Parallel processing for faster scans.
* Direct management options for detected duplicates within the tool.
* Option to use a GUI.
* Capability to detect identical directories.
* Command-line non-interactive mode for automation and scripting.
* Cache invalidation based on usage frequency and age.
* Advanced logging for improved debugging.
* Significant refactoring for efficiency and code clarity.
* Self-contained installer with quick-access shortcuts and context menu integration.
* Option to do a system-wide scan.
* Simple database implementation for caching instead of JSON
* And more!
