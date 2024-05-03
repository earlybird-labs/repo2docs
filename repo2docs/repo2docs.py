import os
import logging
import zipfile
import argparse

from InquirerPy import inquirer
from InquirerPy.validator import PathValidator
from InquirerPy.utils import get_style

from repo2docs.repo_to_text import RepoProcessor
from repo2docs.text_to_docs import TextToDocs
from repo2docs.llm import client_models

from repo2docs import __version__  # Ensure __version__ is imported from the module where it's defined


def main(
    dir_path: str = '.',
    output_file: str = "output.md",
    prompt: str = None,
    doc_type: str = "documentation",
    llm: str = "anthropic",
    model: str = None,
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
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version number and exit."
    )
    
    parser.add_argument(
        "--dir_path",
        help="The directory path to process, defaults to current directory if not provided.",
        default=None
    )
    parser.add_argument(
        "--output_file",
        help="The output file path where the documentation will be saved.",
        default=None,
    )
    parser.add_argument(
        "--prompt",
        help="The prompt to use for generating the documentation.",
        default=None
    )
    parser.add_argument(
        "--type",
        dest="doc_type",
        choices=["documentation", "diagram", "database"],
        default=None,
        help="Specify the type of documentation to generate.",
    )
    parser.add_argument(
        "--llm",
        default=None,
        help="Specify the language model API to use for generating documentation.",
    )
    
    parser.add_argument(
        "--model",
        default=None,
        help="Specify the model to use for generating documentation.",
    )
    
    parser.add_argument(
        "--ignore_dirs", nargs="*", default=[], help="List of directories to ignore."
    )

    args = parser.parse_args()

    style = get_style({
        "questionmark": "#e5c07b",
        "answermark": "#e5c07b",
        "answer": "#61afef",
        "input": "#98c379",
        "question": "",
        "answered_question": "",
        "instruction": "#abb2bf",
        "long_instruction": "#abb2bf",
        "pointer": "#61afef",
        "checkbox": "#98c379",
        "separator": "",
        "skipped": "#5c6370",
        "validator": "",
        "marker": "#e5c07b",
        "fuzzy_prompt": "#c678dd",
        "fuzzy_info": "#abb2bf",
        "fuzzy_border": "#4b5263",
        "fuzzy_match": "#c678dd",
        "spinner_pattern": "#e5c07b",
        "spinner_text": "",
    })

    # Convert all prompts to use InquirerPy
    if args.dir_path is None:
        dir_choice = inquirer.select(
            message="Select the directory to process:",
            choices=["Current directory", "Enter directory"],
            default="Current directory",
            style=style
        ).execute()

        if dir_choice == "Current directory":
            args.dir_path = "."
        elif dir_choice == "Enter directory":
            args.dir_path = inquirer.text(
                message="Enter the directory path to process (leave blank for current directory):",
                validate=PathValidator(is_dir=True, message="Please enter a valid directory path"),
                default="",
                style=style
            ).execute()

    if args.output_file is None:
        args.output_file = inquirer.select(
            message="Select the output file path:",
            choices=["Default (README.md)", "Enter file path"],
            default="Default (README.md)",
            style=style
        ).execute()
        if args.output_file == "Enter file path":
            args.output_file = inquirer.text(
                message="Enter the output file path name:",
                default="",
                style=style
            ).execute()
            if ".md" not in args.output_file:
                args.output_file += ".md"
        else:
            args.output_file = "README.md"

    if args.prompt is None and args.doc_type is None:
        args.prompt = inquirer.select(
            message="Choose from preset prompts or enter a custom prompt:",
            choices=["documentation", "diagram", "database", "Enter custom prompt"],
            default="documentation",
            style=style
        ).execute()
        if args.prompt == "Enter custom prompt":
            args.prompt = inquirer.text(
                message="Enter the custom prompt:",
                default="",
                style=style
            ).execute()
        else:
            args.doc_type = args.prompt
            args.prompt = None

    if args.llm is None:
        args.llm = inquirer.select(
            message="Select the language model API to use:",
            choices=["anthropic", "openai"],
            default="anthropic",
            style=style
        ).execute()
        
    if args.llm == "anthropic":
        args.model = inquirer.select(
            message="Select the model to use:",
            choices=client_models["anthropic"],
            default="claude-3-haiku-20240307",
            style=style
        ).execute()
    elif args.llm == "openai":
        args.model = inquirer.select(
            message="Select the model to use:",
            choices=client_models["openai"],
            default="gpt-4-turbo",
            style=style
        ).execute()

    main(args.dir_path, args.output_file, args.prompt, args.doc_type, args.llm, args.model, args.ignore_dirs)

