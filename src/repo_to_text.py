import sys
import requests
import zipfile
import io
import ast

# import tkinter as tk
# from tkinter import filedialog, simpledialog

class RepoProcessor:
    """A class to process files from a GitHub repository."""

    SUPPORTED_EXTENSIONS = [".py", ".js", ".jsx", ".ts", ".tsx", ".c", ".cpp", ".h", ".hpp"]

    def __init__(self, repo_path: str, output_file: str, ignore_dirs: list = []):
        self.repo_path = repo_path
        self.output_file = output_file
        self.ignore_dirs = ignore_dirs

    def process_repo(self) -> str:
        """Process files from the repository."""
        processed_text = ""
        if self.repo_path.endswith(".zip"):
            processed_text = self._process_zip()
        else:
            processed_text = self._process_url()

        if self.output_file:
            with open(self.output_file, "w", encoding="utf-8") as outfile:
                outfile.write(processed_text)
            print(f"Repository content has been successfully saved to {self.output_file}.")
        else:
            return processed_text

    def _process_zip(self) -> str:
        """Process files from a downloaded GitHub repository zip file and return the processed text."""
        try:
            with zipfile.ZipFile(self.repo_path) as zip_file:
                return self._process_files(zip_file)
        except FileNotFoundError:
            print(f"Failed to find the zip file at {self.repo_path}. Please check the path and try again.")
            sys.exit(1)
        except zipfile.BadZipFile:
            print(f"The file at {self.repo_path} is not a valid zip file. Please check the file and try again.")
            sys.exit(1)

    def _process_url(self) -> str:
        """Process files from a GitHub repository URL and return the processed text."""
        if "/tree/" in self.repo_path:
            self.repo_path = f"https://download-directory.github.io/?{self.repo_path}"

        response = requests.get(f"{self.repo_path}/archive/master.zip")
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        return self._process_files(zip_file)

    def _process_files(self, zip_file: zipfile.ZipFile) -> str:
        """Process files from the zip file and return the processed text."""
        processed_texts = []  # Use a list to accumulate processed texts
        for file_path in zip_file.namelist():
            if self._is_valid_file(file_path):
                file_content = zip_file.read(file_path).decode("utf-8")
                comment_syntax = self._get_comment_syntax(file_path)
                processed_texts.append(f"{comment_syntax} File: {file_path}\n")
                processed_texts.append(self._clean_file_content(file_path, file_content))
                processed_texts.append("\n\n")
        return ''.join(processed_texts)  # Return the accumulated text as a single string

    def _is_valid_file(self, file_path: str) -> bool:
        """Check if the file is valid for processing."""
        return (
            not file_path.endswith("/")
            and any(file_path.endswith(ext) for ext in self.SUPPORTED_EXTENSIONS)
            and self._is_likely_useful_file(file_path)
        )

    
    def _is_likely_useful_file(self, file_path: str) -> bool:
        """Determine if the file is likely to be useful by excluding certain directories and specific file types."""
        excluded_dirs = ["docs", "examples", "tests", "test", "__pycache__", "scripts", "utils", "benchmarks", "node_modules", ".venv"] + self.ignore_dirs
        utility_or_config_files = ["hubconf.py", "setup.py", "package-lock.json"]
        github_workflow_or_docs = ["stale.py", "gen-card-", "write_model_card"]

        return (
            not any(part.startswith(".") for part in file_path.split("/"))
            and "test" not in file_path.lower()
            and not any(f"/{excluded_dir}/" in file_path or file_path.startswith(f"{excluded_dir}/") for excluded_dir in excluded_dirs)
            and not any(file_name in file_path for file_name in utility_or_config_files)
            and not any(doc_file in file_path for doc_file in github_workflow_or_docs)
        )

    def _clean_file_content(self, file_path: str, file_content: str) -> str:
        """Clean and prepare file content for output, using the correct commenting syntax."""
        if file_path.endswith(".py"):
            return self._remove_python_comments_and_docstrings(file_content)
        elif file_path.endswith((".js", ".jsx", ".ts", ".tsx", ".c", ".cpp", ".h", ".hpp")):
            return self._remove_js_ts_comments(file_content)
        else:
            return file_content

    @staticmethod
    def _remove_python_comments_and_docstrings(source: str) -> str:
        """Remove comments and docstrings from Python source code."""
        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and ast.get_docstring(node):
                    node.body = node.body[1:]  # Remove docstring
                elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                    node.value.s = ""  # Remove comments
            return ast.unparse(tree)
        except SyntaxError:
            return source  # Return original source if there's a syntax error

    @staticmethod
    def _remove_js_ts_comments(source: str) -> str:
        """Remove comments from JavaScript or TypeScript source code."""
        lines = source.split('\n')
        clean_lines = []
        in_block_comment = False
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('/*'):
                in_block_comment = True
            if not in_block_comment and not stripped_line.startswith('//'):
                clean_lines.append(line)
            if stripped_line.endswith('*/'):
                in_block_comment = False
                continue  # Skip the line that ends the block comment
        return '\n'.join(clean_lines)
    
    def _get_comment_syntax(self, file_path: str) -> str:
        """Determine the correct comment syntax based on the file extension."""
        if file_path.endswith((".py",)):
            return "#"
        elif file_path.endswith((".js", ".jsx", ".ts", ".tsx", ".c", ".cpp", ".h", ".hpp")):
            return "//"
        else:
            return "#"  # Default to Python comment syntax as a fallback


    # def gui_process_repo(self):
    #     """Process repository using a GUI to select files."""
    #     root = tk.Tk()
    #     root.withdraw()  # We don't want a full GUI, so keep the root window from appearing

    #     # Show an "Open" dialog box and return the path to the selected file
    #     self.repo_path = filedialog.askopenfilename(
    #         title="Select repository ZIP file",
    #         filetypes=(("ZIP files", "*.zip"), ("All files", "*.*"))
    #     )
    #     if not self.repo_path:
    #         print("No file selected. Exiting.")
    #         sys.exit(0)

    #     self.output_file = filedialog.asksaveasfilename(
    #         title="Save output file as...",
    #         defaultextension=".txt",
    #         filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    #     )
    #     if not self.output_file:
    #         print("No output file specified. Exiting.")
    #         sys.exit(0)

    #     self.process_repo()
    #     print(f"Repository content has been successfully saved to {self.output_file}.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process a GitHub repository and output its content to a text file.")
    parser.add_argument("repo_path", nargs='?', default=None, help="The path to the GitHub repository zip file or URL.")
    parser.add_argument("output_file", nargs='?', default=None, help="The output file path where the repository content will be saved.")
    parser.add_argument("--gui", action="store_true", help="Enable GUI mode for file selection.")
    parser.add_argument("--format", choices=["txt", "md"], default="txt", help="Specify the output file format (txt or md).")


    args = parser.parse_args()
    
    output_extension = ".md" if args.format == "md" else ".txt"
    if args.output_file and not args.output_file.endswith(output_extension):
        args.output_file += output_extension

    if args.gui:
        processor = RepoProcessor(None, None)  # Initialize with None since we'll set these via GUI
        processor.gui_process_repo()
    else:
        if not args.repo_path or not args.output_file:
            parser.print_help()
            sys.exit(1)
        processor = RepoProcessor(args.repo_path, args.output_file)
        processor.process_repo()