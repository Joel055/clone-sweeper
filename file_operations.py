import os 
import hashlib
import json
import cache_manager as cm
#import multiprocessing

# Using a class instead of utility functions to preserve state / multiple scans at once 
class FileOperations:
    """Manages file operations for CloneSweeper, including directory traversal and duplicate detection."""
    def __init__(self, settings, pbar = None):
        self.settings = settings
        self.pbar = pbar
        self.error_dump = []
        self.detected = False
        # Initializes cache object with custom metadata key for hash
        self.cache = cm.CacheOperations(["hash_algorithm"])
        self.cache.load()
        self.validate_hash_algo()

    def scan_directory(self, scan_path, recursive=False, top_level=True):
        for path in scan_path:
            for entry in os.scandir(path):
                try:
                    filename = entry.name

                    if self._omit(entry): # Resolve the path once instead of everytime in the function
                        self._update_pbar(entry, True)
                        continue

                    in_cache = self._check_in_cache(entry) # Checks for an identical match

                    if entry.is_file():
                        self._update_pbar(entry, in_cache)

                        if not in_cache:
                            if filename not in self.cache.data: # Creates an empty list to hold a dictionary for each name instance, if no other instances exist.
                                self.cache.data[filename] = [] 
                            
                            self.cache.data[filename].append({
                                self.settings["hash_algorithm"]: self._calculate_hash(entry),
                                "PATH": entry.path,
                                "MODIFIED_TIME": entry.stat().st_mtime
                            })
                
                    elif entry.is_dir() and recursive: # Calls function recusively to perform check on subdirecories if the recursive flag is True
                        self.scan_directory([entry.path], True, False)

                except (PermissionError, IOError) as error:
                    self.error_dump.append(str(error)) # Make a logfile instead, maybe include cacheoperations
                    continue
        
        if top_level:
            self.cache.metadata["hash_algorithm"] = self.settings["hash_algorithm"]
            self.cache.write() # Only write at top level to avoid corruption and to make sure a complete dataset is available.
            self._identify_duplicates()

    def _calculate_hash(self, file_entry):
        algorithm = self.settings.get("hash_algorithm", "md5").lower()

        hash_obj = getattr(hashlib, algorithm)()

        with open(file_entry.path, "rb") as file: # Read files in binary to eliminate etc newline differences between OS's.
            while True:
                chunk = file.read(self.settings["hash_chunk_size"])

                if not chunk:
                    break

                hash_obj.update(chunk) 
  
        return hash_obj.hexdigest() 

    def _identify_duplicates(self): # Needs tweaking for multiple runs, and persistant detected duplicates.
        duplicates = {}
        hashes = {}

        for _, name_instances in self.cache.data.items():
            for instance in name_instances:
                hash = instance[self.settings["hash_algorithm"]]
                path = instance["PATH"]

                if hash in hashes:
                    if hash not in duplicates:
                        duplicates[hash] = [hashes[hash]]

                    duplicates[hash].append(path)
                else:
                    hashes[hash] = path

        if duplicates:
            self.detected = True
            with open("./duplicates.json", "w") as file:
                json.dump(duplicates, file, indent = 4)

    def _omit(self, entry): 
        # Resolve environment variables and convert to absolute paths for the paths to skip.
        resolved_skip_paths = []

        for skip_path in self.settings["default_paths_skip"] + self.settings["user_paths_skip"]:
            resolved_path = os.path.abspath(os.path.expandvars(skip_path))
            resolved_skip_paths.append(resolved_path)

        # Check if the entrys path is in the list of paths to skip.
        if os.path.abspath(entry.path) in resolved_skip_paths:
            return True
        
        # Check filesize
        if entry.stat().st_size  / (1024**2) > self.settings["max_file_size_mb"]:
            return True

        # Extract file name and extension to check if it should be skipped.
        name_no_ext, file_extension = os.path.splitext(entry.name)

        if entry.name in self.settings["user_filenames_skip"] or name_no_ext in self.settings["user_filenames_skip"]:
            return True

        if file_extension:
            return file_extension in self.settings["default_exts_skip"] + self.settings["user_exts_skip"]
                
    def _check_in_cache(self, entry):
        cached = False
        if entry.name in self.cache.data:

            # Compares the filedata to the corresponding key in cache to see if its the same.
            for file_info in self.cache.data[entry.name]:
                if file_info["PATH"] == entry.path and file_info["MODIFIED_TIME"] == entry.stat().st_mtime:
                    cached = True

        return cached
                
    def _update_pbar(self, entry, skipped=False):
        if self.pbar is not None:
            self.pbar.set_description(f"{entry.name:<30}: {'SKIPPING' if skipped else 'CALCULATING HASH'}")
            self.pbar.update(1)

            #ONLY FOR DEBUG
            #time.sleep(0.05)
            #entry_verdict.append(f"{filename:<30}: {'SKIPPING' if in_cache else 'CALCULATING HASH'}")

    def print_data(self):
        if self.detected:
            print(f"\n\nSCAN FINISHED: See \"{os.getcwd()}\\duplicates.json\" for identified duplicates.")
        else:
            print("\n\nSCAN FINISHED: No duplicates were detected.")

        if len(self.error_dump) > 0:
            print("\n\nErrors encountered during the scan:")

            for error in self.error_dump:
                print(f"\n   - {error}") 

        #ONLY FOR DEBUG
        #for item in entry_verdict:
        #    print("\n", item) 

    def validate_hash_algo(self): #move to main?
        if self.settings["hash_algorithm"] not in hashlib.algorithms_available:
            print(f"\nUnsupported hashing algorithm: ('{self.settings["hash_algorithm"]}') defaulting to md5")
            self.settings["hash_algorithm"] = "md5"
        
        # Check what hash algorithm was last used and compare to the one in settings.
        cache_hash = self.cache.metadata["hash_algorithm"]

        if self.settings["hash_algorithm"] != cache_hash and cache_hash != "":
            print("\nHashing algorithm changed, clearing cache.")
            self.cache.clear()
