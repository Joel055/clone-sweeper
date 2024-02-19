import os
import platform
import ctypes
import json
import re
from tqdm import tqdm
from file_operations import FileOperations
from menu import Menu


class CloneSweeper:
    """Entry point and core controller for the CloneSweeper application."""
    def __init__(self):
        self.settings_path = ".\\settings.json"
        self.settings = self._load_settings()
        self.fo = None
        # Move cache here?

    def run(self):
        print ("\nDisclaimer: Use at your own risk. No warranty is provided. The creator is not liable for any damages.")
        self._is_elevated()
        self.fo = FileOperations(self.settings)

        option_menu = Menu()
        option_menu.add_option("Exclude Paths", self._exclude_paths)
        option_menu.add_option("Exclude Extensions", self._exclude_extensions)
        option_menu.add_option("Exclude Filenames", self._exclude_filenames)
        option_menu.add_option("Clear user defined exclusions", self._clear_user_exclusions)
        option_menu.add_option("Back", option_menu.exit)

        main_menu = Menu("CLONE-SWEEPER", f"Current Directory: {os.getcwd()}", "Choice", True)
        main_menu.add_option("Start", self._prepare_scan)
        main_menu.add_option("Clear Cache", self.fo.cache.clear)
        main_menu.add_option("Clear duplicates list", self._clear_duplicates)
        main_menu.add_option("Settings", option_menu.display)
        main_menu.add_option("View JSON Settings", self._show_settings)
        main_menu.add_option("Exit", main_menu.exit)
        main_menu.display()

    def _prepare_scan(self):
        scan_recursive = self._validate_input("\nRecursive scan(Y/N): ")

        while True:
            dir_input = input("\nEnter directory path(s) to scan, leave blank for current directory (split with ','): ")      
            
            if dir_input == "": # Scan current directory if empty input
                self._start_scan([os.getcwd()], scan_recursive)
                break
            else:
                validated_paths = self._validate_directories(dir_input)

                if validated_paths:
                    non_redundant_paths = self._redundancy_check(validated_paths, scan_recursive)
                    self._start_scan(non_redundant_paths, scan_recursive)
                    break

    def _start_scan(self, dir_path, scan_recursive):
        print("\n")
        #move FileOperation object creation here

        # Indeterminate progress bar
        with tqdm(position = 0, leave = True, unit = " files") as pbar:
            self.fo.pbar = pbar 
            self.fo.scan_directory(dir_path, scan_recursive)

        self.fo.print_data()

    def _clear_duplicates(self):
        try:
            with open("./duplicates.json", "w") as file:
                json.dump({}, file, indent = 4)

            print("\nDuplicates cleared.")

        except Exception as e:  
            print(f"\nCould not clear duplicate file ({e}).")  # Fix mroe specific errors

    def _validate_directories(self, dir_input):
        dir_paths = self._clean_and_split(dir_input)
        absolute_paths = [os.path.abspath(dir) for dir in dir_paths]
        invalid_dir = False

        for directory in absolute_paths: # Checks so that the input contains valid directories
            if not os.path.isdir(directory):
                print(f"\n\"{directory}\" is not a valid path or directory.")
                invalid_dir = True 
        
        if invalid_dir:
            return []
        else:
            return absolute_paths
            
    def _redundancy_check(self, paths, scan_recursive):
        exclusions = set()

        # Check for redundant paths by comparing them to an eventual common path
        if len(paths) > 1 and scan_recursive:
            for i, dir1 in enumerate(paths):
                for dir2 in paths[i+1:]:
                    try: 
                        common_path = os.path.commonpath([dir1, dir2])

                        if dir1 == common_path:
                            exclusions.add(dir2)
                        elif dir2 == common_path:
                            exclusions.add(dir1)

                    except ValueError: # If compared paths are on different drives 
                        pass

            print()

            if exclusions:
                print("Following path(s) are redundant and will be exluded from the scan:\n")

                for e in exclusions:
                    print(f"\t\"{e}\"")
                    paths.remove(e)
        
        print(f"\n\nSCAN PATHS(s): {paths}")
        return paths

    def _validate_input(self, prompt):
        while True:
            user_input = input(prompt).lower()

            if user_input in ("y", "n"):
                return user_input == "y"
            
            print("\nInvalid input.")

    def _load_settings(self):
        try:
            with open(self.settings_path, "r") as file:
                return json.load(file)
            
        except Exception as e:
            print(f"\nWARNING SETTINGS FAILED TO LOAD: {e}")

    def _write_settings(self, location, arg):
        settings = self._load_settings()
        exclusion_added = False

        for item in arg:
            if item not in settings[location]:
                settings[location].append(item)
                exclusion_added = True
            else:
                print(f"\nExclusion ('{item}') already exists.")

        if exclusion_added:    
            try:
                with open(self.settings_path, "w") as file:
                    json.dump(settings, file, indent = 4)
                
                print("\nExclusion(s) succesfully added.")
                self.settings = settings # Adds new settings to instancevar

            except Exception as e:
                print(f"\nFailed to write to settings: {e}")

    def _show_settings(self):
        print(f"\nCurrent Settings: {json.dumps(self.settings, indent = 4)}")

    def _clear_user_exclusions(self):
        settings = self._load_settings()
        settings["user_exts_skip"] = []
        settings["user_paths_skip"] = []
        settings["user_filenames_skip"] = []
        
        try:
            with open(self.settings_path, "w") as file:
                json.dump(settings, file, indent=4)

            print("\nUser defined exclusions successfully cleared.")
            self.settings = settings

        except Exception as e:
            print(f"\nFailed to clear user defined exclusions: {e}")

    def _exclude_paths(self):
        while True:
            paths = input("\nPath(s) to exclude (split with ','): ")
            validated_paths = self._validate_directories(paths)

            if validated_paths:
                self._write_settings("user_paths_skip", validated_paths)
                break

    def _exclude_extensions(self):
        while True:
            ext_input = input("\nExtension(s) to exclude (split with ','): ")
            extensions = self._clean_and_split(ext_input)
            invalid_extension = False

            for extension in extensions:
                if not extension.startswith(".") or len(extension) > 8:
                    print(f"\nInvalid extension ('{extension}'), make sure it starts with a \".\" and is less than 9 characters.")
                    invalid_extension = True

            if not invalid_extension:
                self._write_settings("user_exts_skip", extensions)
                break

    def _exclude_filenames(self):
        print("\nTo exclude all filetypes, omit the file extension ('report' excludes 'report.txt', 'report.pdf etc.)")
        
        while True:
            name_input = input("\nFilename(s) to exclude (split with ','): ")
            filenames = self._clean_and_split(name_input)
            invalid_filename = False

            invalid_chars = r'[<>:"/\\|?*]' 
            for filename in filenames:
                # Forbidden characters and max filelength
                if re.search(invalid_chars, filename) or len(filename) > 255:
                    print(f"\n'{filename}' is invalid. Avoid restricted symbols and keep within 255 characters.")
                    invalid_filename = True
            
            if not invalid_filename:
                self._write_settings("user_filenames_skip", filenames)
                break

    def _clean_and_split(self, input_string, delimiter = ","):
        return [item.strip() for item in input_string.split(delimiter) if item.strip()]

    def _is_elevated(self):
        os_name = platform.system()

        match os_name:
            case "Windows":
                if ctypes.windll.shell32.IsUserAnAdmin():
                    return True
                else:
                    print("\nNon-administrative privileges detected, run as administrator for best experience.")

            case "Linux", "Darwin":
                if os.geteuid() == 0: # Check if running as root
                    return True
                else:
                    print("\nNon-administrative privileges detected, run with sudo for best experience.")

        
if __name__ == "__main__":
    app = CloneSweeper()
    app.run()
