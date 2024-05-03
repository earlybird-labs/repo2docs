import os
import logging
import zipfile
import argparse
import sys

from repo2docs.repo_to_text import RepoProcessor
from repo2docs.text_to_docs import TextToDocs

def main(
    dir_path: str = '.',
    output_file: str = "output.md",
    prompt: str = None,
    doc_type: str = "documentation",
    llm: str = "openai",
    ignore_dirs: list = [],
):
    # Create a temporary zip file from the specified directory
    repo_zip_path = os.path.join(os.getcwd(), 'repository.zip')
    with zipfile.ZipFile(repo_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(dir_path, '..')))

    # Process the .zip file to get repository text
    repo_processor = RepoProcessor(
        repo_zip_path, None, ignore_dirs
    )
    repo_text = repo_processor.process_repo()

    logging.info(f"Repository text has been successfully processed.")
    
    # Convert the repository text to documentation
    text_to_docs = TextToDocs(llm)
    if prompt:
        docs_content = text_to_docs.generate_custom(repo_text, prompt)
    elif doc_type == "diagram":
        docs_content = text_to_docs.generate_diagram(repo_text)
    elif doc_type == "database":
        docs_content = text_to_docs.generate_database(repo_text)
    elif doc_type == "mobile":
        docs_content = text_to_docs.generate_mobile(repo_text)
    else:
        docs_content = text_to_docs.generate_docs(repo_text)

    if not os.path.dirname(output_file):
        output_file = os.path.join(os.getcwd(), output_file)

    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write(docs_content)
    logging.info(f"Documentation has been successfully saved to {output_file}.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Convert a directory into documentation."
    )
    parser.add_argument(
        "--dir_path", 
        help="The directory path to process, defaults to current directory if not provided.",
        default="."
    )
    parser.add_argument(
        "--output_file",
        help="The output file path where the documentation will be saved.",
        default="output.md",
    )
    
    parser.add_argument(
        "--prompt",
        help="The prompt to use for generating the documentation.",
        default=None
    )
    
    parser.add_argument(
        "--type",
        choices=["documentation", "diagram", "database", "mobile"],
        default="documentation",
        help="Specify the type of documentation to generate.",
    )
    parser.add_argument(
        "--llm",
        choices=["openai", "anthropic"],
        default="openai",
        help="Specify the language model API to use for generating documentation.",
    )
    parser.add_argument(
        "--ignore_dirs", nargs="*", default=[], help="List of directories to ignore."
    )

    args = parser.parse_args()

    main(args.dir_path, args.output_file, args.prompt, args.type, args.llm, args.ignore_dirs)

