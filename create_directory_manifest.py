"""
Create a project manifest (directory tree) as Markdown.
Generic utility: point at any folder, get a tree + optional exclusions.
"""
import os
from datetime import datetime


def create_project_manifest(root_path, output_file, exclude_folders=None):
    if exclude_folders is None:
        exclude_folders = []

    def scan_directory(path, indent_level=0):
        items = []
        try:
            entries = os.listdir(path)
            entries = [e for e in entries if e not in exclude_folders]
            dirs = [e for e in entries if os.path.isdir(os.path.join(path, e))]
            files = [e for e in entries if os.path.isfile(os.path.join(path, e))]
            dirs.sort()
            files.sort()

            for name in dirs:
                if name.startswith(".") or name == "__pycache__":
                    continue
                items.append("│   " * indent_level + "├── " + name + "/")
                items.extend(scan_directory(os.path.join(path, name), indent_level + 1))

            for name in files:
                if name.startswith("."):
                    continue
                items.append("│   " * indent_level + "├── " + name)
        except PermissionError:
            items.append("│   " * indent_level + "├── [Permission Denied]")
        except Exception as e:
            items.append("│   " * indent_level + f"├── [Error: {str(e)}]")
        return items

    manifest_content = [
        "# Project Structure Manifest",
        f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# Excluded folders: {', '.join(exclude_folders) if exclude_folders else 'None'}\n",
        "```plaintext",
        root_path + "/",
    ]
    manifest_content.extend(scan_directory(root_path))
    manifest_content.append("```\n")
    manifest_content.extend([
        "## File Purposes",
        "*(Add descriptions for key files and directories here)*\n",
        "### Key Directories",
        "- Add directory purposes here\n",
        "### Key Files",
        "- Add file descriptions here\n",
        "## Notes",
        "- This structure was automatically generated",
        f"- Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Excluded folders: {', '.join(exclude_folders) if exclude_folders else 'None'}",
    ])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(manifest_content))
    print(f"Manifest successfully created at: {output_file}")


if __name__ == "__main__":
    project_path = input("Enter the project directory path: ").strip()
    output_path = input("Enter the output file path (e.g., manifest.md): ").strip()
    exclude_input = input("Enter folder names to exclude (comma-separated), or Enter for none: ").strip()
    exclude_folders = [x.strip() for x in exclude_input.split(",")] if exclude_input else []

    if os.path.exists(project_path):
        create_project_manifest(project_path, output_path, exclude_folders)
    else:
        print("Error: The specified directory does not exist.")
