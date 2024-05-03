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
    llm: str = "anthropic",
    ignore_dirs: list = [],
):
    # Create a temporary zip file from the specified directory
    repo_zip_path = os.path.join(os.getcwd(), 'repository.zip')
    if not os.path.exists(repo_zip_path):
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
    
    if ":" in llm:
        llm, model = llm.split(":")
    else:
        model = None
    
    # Convert the repository text to documentation
    text_to_docs = TextToDocs(llm, model)
    docs_content = text_to_docs.generate_docs(repo_text, doc_type, prompt)

    if not os.path.dirname(output_file):
        output_file = os.path.join(os.getcwd(), output_file)

    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write(docs_content)
    logging.info(f"Documentation has been successfully saved to {output_file}.")




def run():

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
        dest="doc_type",  # Ensure this matches the parameter name in main
        choices=["documentation", "diagram", "database", "mobile"],
        default="documentation",
        help="Specify the type of documentation to generate.",
    )
    parser.add_argument(
        "--llm",
        default="anthropic",
        help="Specify the language model API to use for generating documentation.",
    )
    parser.add_argument(
        "--ignore_dirs", nargs="*", default=[], help="List of directories to ignore."
    )

    args = parser.parse_args()

    main(args.dir_path, args.output_file, args.prompt, args.doc_type, args.llm, args.ignore_dirs)

