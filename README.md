# find_remove_duplicate_files
Multithreaded python tool to find duplicate files, with option to delete them.

Example:
```
$ python3 find_dup.py .  
Walking dirs..
Duplicate found: ./.git/refs/heads/main

Original: ./.git/refs/remotes/origin/main

Duplicate found: ./.git/logs/refs/heads/main

Original: ./.git/logs/HEAD

Duplicates found. Total files scanned: 38, Total duplicates: 2.
Duplicate files:
./.git/refs/heads/main
./.git/logs/refs/heads/main

Total space used by the files: 0.00045490264892578125 Megabytes
```
