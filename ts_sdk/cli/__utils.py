import os
import zipfile

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def zipdir(path: str, z: zipfile.ZipFile):
    for root, dirs, files in os.walk(path):
        for file in files:
            if not os.path.basename(file).startswith('.'):
                local_path = os.path.join(root, file)
                zip_path = os.path.relpath(os.path.join(root, file), os.path.join(path))
                z.write(local_path, zip_path)
