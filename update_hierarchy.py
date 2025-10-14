import os

def generate_tree(directory, prefix="", ignored_items=None, output=None):
    if ignored_items is None:
        ignored_items = {'.git', '__pycache__', '.pytest_cache', 'node_modules', 'migrations', 'staticfiles', 'media', 'logs', 'certs', 'lobengula', '.python-version', 'uv.lock', 'lobengula.egg-info'}
    try:
        items = sorted([item for item in os.listdir(directory) if item not in ignored_items and not item.startswith('.')])
        for i, item in enumerate(items):
            full_path = os.path.join(directory, item)
            is_last = i == len(items) - 1
            connector = "+-- " if is_last else "|-- "
            line = prefix + connector + item + "\n"
            if output:
                output.write(line)
            else:
                print(line, end="")
            if os.path.isdir(full_path):
                extension = "    " if is_last else "|   "
                generate_tree(full_path, prefix + extension, ignored_items, output)
    except PermissionError:
        pass

if __name__ == "__main__":
    with open("SYSTEM_FILE_HIERARCHY.md", "w", encoding="utf-8") as f:
        f.write("# Retail Management System - Complete File Hierarchy\n\n")
        f.write("## Project Root Structure\n")
        f.write("```\n")
        f.write("retail_management_system/\n")
        generate_tree(".", "|-- ", output=f)
        f.write("```\n")
