import pathlib, difflib
cur=pathlib.Path('aetherra_hub_server.py').read_text(errors='ignore').splitlines()
clean=pathlib.Path('clean_hub_tmp.py').read_text(errors='ignore').splitlines()
for i,l in enumerate(difflib.unified_diff(clean,cur,'HEAD','WORKING')):
    print(l)
    if i>300: break
