import os
import sys
import requests
import zipfile
import io

import ast
import esprima
from pycparser import c_parser, c_ast


class RepoProcessor:
    """A class to process files from a GitHub repository."""

    SUPPORTED_EXTENSIONS = [
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
    ]

    def __init__(self, repo_path: str, output_file: str, ignore_dirs: list = []):
        self.repo_path = repo_path
        self.output_file = output_file
        self.ignore_dirs = ignore_dirs

    def process_repo(self) -> str:
        """Process files from the repository."""
        if self.repo_path.startswith("http"):
            return self._process_url()
        elif self.repo_path.endswith(".zip"):
            return self._process_zip()
        else:
            return self._process_directory()

    def _process_directory(self) -> str:
        """Process files from a directory and return the processed text."""
        processed_texts = []

        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_valid_file(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                    comment_syntax = self._get_comment_syntax(file_path)
                    relative_file_path = os.path.relpath(file_path, self.repo_path)
                    processed_texts.append(
                        f"{comment_syntax} File: {relative_file_path}\n"
                    )
                    cleaned_content = self._clean_file_content(file_path, file_content)
                    processed_texts.append(cleaned_content)
                    processed_texts.append("\n\n")

        return "".join(processed_texts)

    def _process_url(self) -> str:
        """Process files from a GitHub repository URL and return the processed text."""
        if "/tree/" in self.repo_path:
            self.repo_path = f"https://download-directory.github.io/?{self.repo_path}"

        response = requests.get(f"{self.repo_path}/archive/master.zip")
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        return self._process_files(zip_file)

    def _process_zip(self) -> str:
        """Process files from a downloaded GitHub repository zip file and return the processed text."""
        try:
            with zipfile.ZipFile(self.repo_path) as zip_file:
                return self._process_files(zip_file)
        except FileNotFoundError:
            print(
                f"Failed to find the zip file at {self.repo_path}. Please check the path and try again."
            )
            sys.exit(1)
        except zipfile.BadZipFile:
            print(
                f"The file at {self.repo_path} is not a valid zip file. Please check the file and try again."
            )
            sys.exit(1)

    def _process_files(self, zip_file: zipfile.ZipFile) -> str:
        """Process files from the zip file and return the processed text."""
        processed_texts = []
        for file_path in zip_file.namelist():
            if self._is_valid_file(file_path):
                file_content = zip_file.read(file_path).decode("utf-8")
                comment_syntax = self._get_comment_syntax(file_path)
                processed_texts.append(f"{comment_syntax} File: {file_path}\n")
                processed_texts.append(
                    self._clean_file_content(file_path, file_content)
                )
                processed_texts.append("\n\n")
        return "".join(processed_texts)

    def _get_comment_syntax(self, file_path: str) -> str:
        """Get the comment syntax based on the file extension."""
        _, ext = os.path.splitext(file_path)
        if ext in [".py"]:
            return "#"
        elif ext in [".js", ".jsx", ".ts", ".tsx", ".c", ".cpp", ".h", ".hpp"]:
            return "//"
        else:
            return ""

    def _clean_file_content(self, file_path: str, file_content: str) -> str:
        """Clean the file content by removing unnecessary parts and excessive line breaks."""
        _, ext = os.path.splitext(file_path)
        if ext == ".py":
            cleaned_content = self._clean_python_file(file_content)
        elif ext in [".js", ".jsx", ".ts", ".tsx"]:
            cleaned_content = self._clean_javascript_file(file_content)
        elif ext in [".c", ".cpp", ".h", ".hpp"]:
            cleaned_content = self._clean_c_cpp_file(file_content)
        else:
            cleaned_content = file_content

        cleaned_content = self._remove_excessive_line_breaks(cleaned_content)
        return cleaned_content

    def _remove_excessive_line_breaks(self, content: str) -> str:
        """Remove three or more consecutive line breaks from the content."""
        import re

        return re.sub(r"\n{3,}", "\n\n", content)

    def _clean_python_file(self, file_content: str) -> str:
        """Clean the Python file content by removing unnecessary parts."""
        tree = ast.parse(file_content)
        cleaned_lines = []

        for node in ast.walk(tree):
            if isinstance(
                node,
                (ast.Import, ast.ImportFrom, ast.ClassDef, ast.FunctionDef, ast.Assign),
            ):
                cleaned_lines.append(ast.unparse(node))

        return "\n".join(cleaned_lines)

    def _clean_javascript_file(self, file_content: str) -> str:
        """Clean the JavaScript/TypeScript file content by removing unnecessary parts."""
        try:
            tree = esprima.parseScript(file_content, loc=True)
            cleaned_lines = []

            for node in tree.body:
                if isinstance(
                    node,
                    (
                        esprima.nodes.FunctionDeclaration,
                        esprima.nodes.ClassDeclaration,
                        esprima.nodes.VariableDeclaration,
                    ),
                ):
                    start_line = node.loc.start.line - 1
                    end_line = node.loc.end.line
                    cleaned_lines.extend(file_content.split("\n")[start_line:end_line])

            return "\n".join(cleaned_lines)
        except Exception as e:
            # If parsing fails, return the cleaned file content without comments
            return self._remove_comments(file_content)

    def _remove_comments(self, file_content: str) -> str:
        """Remove comments from the file content using regex."""
        import re

        # Regex patterns to match single line and multi-line comments
        patterns = [
            r"//.*",  # Single line comments
            r"/\*[\s\S]*?\*/",  # Multi-line comments in C, C++, JavaScript
            r"#.*",  # Single line comments in Python
            r"\'\'\'[\s\S]*?\'\'\'",  # Multi-line comments in Python with triple single quotes
            r"\"\"\"[\s\S]*?\"\"\"",  # Multi-line comments in Python with triple double quotes
            r"{/\*[\s\S]*?\*/}",  # Multi-line comments in JSX within curly braces
            r"{//.*?}",  # Single line comments in JSX within curly braces
        ]

        # Combine all patterns into a single pattern
        combined_pattern = "|".join(patterns)

        # Use regex to substitute matched patterns with an empty string
        cleaned_content = re.sub(combined_pattern, "", file_content, flags=re.MULTILINE)

        return cleaned_content

    def _clean_c_cpp_file(self, file_content: str) -> str:
        """Clean the C/C++ file content by removing unnecessary parts."""
        try:
            parser = c_parser.CParser()
            ast = parser.parse(file_content)
            cleaned_lines = []

            for node in ast:
                if isinstance(
                    node,
                    (
                        c_ast.FuncDef,
                        c_ast.Struct,
                        c_ast.Union,
                        c_ast.Enum,
                        c_ast.Typedef,
                    ),
                ):
                    start_line = node.coord.line - 1
                    end_line = self._find_end_line(node, file_content)
                    cleaned_lines.extend(file_content.split("\n")[start_line:end_line])

            return "\n".join(cleaned_lines)
        except c_parser.ParseError:
            # If parsing fails, return the original file content
            return file_content

    def _find_end_line(self, node, file_content: str) -> int:
        """Find the end line number for a given node in the C/C++ file."""
        lines = file_content.split("\n")
        end_line = node.coord.line

        for i in range(node.coord.line, len(lines)):
            if lines[i].strip().endswith(";") or lines[i].strip().endswith("}"):
                end_line = i + 1
                break

        return end_line

    def _is_valid_file(self, file_path: str) -> bool:
        """Check if the file is valid for processing."""
        is_valid = (
            not file_path.endswith("/")
            and any(file_path.endswith(ext) for ext in self.SUPPORTED_EXTENSIONS)
            and self._is_likely_useful_file(file_path)
        )
        return is_valid

    def _is_likely_useful_file(self, file_path: str) -> bool:
        """Determine if the file is likely to be useful by excluding certain directories and specific file types."""
        excluded_dirs = [
            "docs",
            "examples",
            "tests",
            "test",
            "__pycache__",
            "scripts",
            "utils",
            "benchmarks",
            "node_modules",
            "env",
            "venv",
            ".venv",
        ]
        utility_or_config_files = ["hubconf.py", "setup.py", "package-lock.json"]
        github_workflow_or_docs = ["stale.py", "gen-card-", "write_model_card"]

        relative_file_path = os.path.relpath(file_path, self.repo_path)

        return (
            not any(
                part.startswith(".") for part in relative_file_path.split(os.path.sep)
            )
            and "test" not in relative_file_path.lower()
            and not any(
                os.path.sep + excluded_dir + os.path.sep in relative_file_path
                or relative_file_path.startswith(excluded_dir + os.path.sep)
                for excluded_dir in excluded_dirs
            )
            and not any(
                file_name in relative_file_path for file_name in utility_or_config_files
            )
            and not any(
                doc_file in relative_file_path for doc_file in github_workflow_or_docs
            )
        )
