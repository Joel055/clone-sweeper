import json
from datetime import datetime
from typing import List, Optional


class CacheOperations:
    """Manages a cache system for storing and retrieving data efficiently.

    This class provides functionalities to load data from a cache file, write updates to the cache,
    and clear the cache contents. It supports custom metadata for enhanced cache management. """
    def __init__(self, metadata_keys: Optional[List[str]] = None,  file_path: Optional[str] = "./cache.json"):
        self.cache_path = file_path
        self.default_metadata = {
            "time_created": self._current_time(),
            "time_updated": None,
            "times_loaded": 0
            }
        if metadata_keys: # Custom defined metadata keys
            for key in metadata_keys:
                self.default_metadata[key] = ""

        self.data = {}
        self.metadata = self.default_metadata.copy()

    def __str__(self):
        return f"CacheOperations object with {len(self.data)} items in cache at {self.cache_path}"
    
    def _current_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def load(self):
        try: 
            with open(self.cache_path, "r") as file:
                cache_content = json.load(file)

                bad_keys = [] # Checks if metadata keys exist in existing cache
                for key in self.metadata.keys():
                    if key not in cache_content.get("metadata"):
                        bad_keys.append(key)
                
                if bad_keys: 
                    raise KeyError(bad_keys)

                self.metadata = cache_content.get("metadata")
                self.data = cache_content.get("data")
                self.metadata["times_loaded"] += 1 # Write this to cache immediately or after?
                
        except FileNotFoundError:
            print("\nCache file not found. Initializing a new cache.")
            self.write()

        except json.JSONDecodeError:
            print("\nCache file is corrupt (invalid JSON). Regenerating cache.")
            self.write()
        
        except KeyError as e:
            print(f"\nInconsistent metadata key(s) {e} passed. Regenerating cache with keys.")
            self.write()

    def write(self):
        self.metadata["time_updated"] = self._current_time()
        cache_structure = {
            "metadata": self.metadata,
            "data": self.data
            }
        try:
            with open(self.cache_path, "w") as file:
                json.dump(cache_structure, file, indent = 4)

        except Exception as e:
            print(f"\nCould not write cache due to the following exception: {e}")
    
    def clear(self):
        self.metadata = self.default_metadata.copy()
        self.data = {}
        self.write()
        print("\nCache cleared.")

