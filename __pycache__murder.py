import os
import shutil

def delete_pycache(dir_path):
    for root, dirs, files in os.walk(dir_path):
        if "__pycache__" in dirs:
            pycache_dir = os.path.join(root, "__pycache__")
            print(f"Deleting {pycache_dir}")
            shutil.rmtree(pycache_dir)

if __name__ == "__main__":
    dir_path = "."
    delete_pycache(dir_path)
