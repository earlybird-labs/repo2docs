import os
import logging

from repo_to_text import RepoProcessor
from text_to_docs import TextToDocs

def main(repo_zip_path: str, output_file: str, doc_type: str = "documentation", llm: str = "openai",  ignore_dirs: list = []):
    # Process the .zip file to get repository text
    repo_processor = RepoProcessor(repo_zip_path, None, ignore_dirs)  # Add ignore_dirs here
    repo_text = repo_processor.process_repo()
    
    
    logging.info(f"Repository text has been successfully processed.")

    # Convert the repository text to documentation
    text_to_docs = TextToDocs(llm)
    
    if doc_type == "diagram":
        docs_content = text_to_docs.generate_diagram(repo_text)
    elif doc_type == "database":
        docs_content = text_to_docs.generate_database(repo_text)
    else:
        docs_content = text_to_docs.generate_docs(repo_text)

    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write(docs_content)
    logging.info(f"Documentation has been successfully saved to {output_file}.")

if __name__ == "__main__":
    import argparse
    
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(description="Convert a GitHub repository .zip file into documentation.")
    parser.add_argument("repo_zip_path", help="The path to the GitHub repository .zip file.")
    parser.add_argument("output_file", help="The output file path where the documentation will be saved.", default="docs.md")
    parser.add_argument("--type", choices=["documentation", "diagram", "database"], default="documentation", help="Specify the type of documentation to generate (documentation or diagram).")
    parser.add_argument("--llm", choices=["openai", "anthropic"], default="openai", help="Specify the language model API to use for generating documentation.")
    parser.add_argument("--ignore_dirs", nargs='*', default=[], help="List of directories to ignore.")

    args = parser.parse_args()

    main(args.repo_zip_path, args.output_file, args.type, args.llm, args.ignore_dirs)
