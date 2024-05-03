import os
import logging
import zipfile
import argparse

from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import radiolist_dialog


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
        choices=["documentation", "diagram", "database", "mobile"],
        default=None,
        help="Specify the type of documentation to generate.",
    )
    parser.add_argument(
        "--llm",
        default=None,
        help="Specify the language model API to use for generating documentation.",
    )
    parser.add_argument(
        "--ignore_dirs", nargs="*", default=[], help="List of directories to ignore."
    )

    args = parser.parse_args()

    style = Style.from_dict({
        'prompt': '#0031C5',
        'default': '#0B8800',
    })

    # Prompt for input if arguments are not provided
    if args.dir_path is None:
        args.dir_path = prompt(FormattedText([
            ('class:prompt', 'Enter the directory path to process '),
            ('class:default', '(leave blank for current directory)'),
            ('class:prompt', ': ')
        ]), default="", style=style)
    if args.dir_path == "":
        args.dir_path = "."
        
    if args.output_file is None:
        args.output_file = prompt(FormattedText([
            ('class:prompt', 'Enter the output file path '),
            ('class:default', '(leave blank for output.md)'),
            ('class:prompt', ': ')
        ]), default="", style=style)
    if args.output_file == "":
        args.output_file = "output.md"
        
    if args.prompt is None:
        args.prompt = prompt(FormattedText([
            ('class:prompt', 'Enter the prompt for generating documentation: ')
            ('class:default', '(leave blank for presets)'),
            ('class:prompt', ': ')
        ]), default="", style=style)
        
    if args.prompt is "":
        args.doc_type = prompt(FormattedText([
            ('class:prompt', 'Enter the type of documentation to generate '),
            ('class:default', '(default: documentation | diagram | database | mobile)'),
            ('class:prompt', ': ')
        ]), default="documentation", style=style)
        args.doc_type = args.doc_type.lower().strip()
        
    if args.llm is None:
        args.llm = prompt(FormattedText([
            ('class:prompt', 'Enter the language model API to use '),
            ('class:default', '(default: anthropic)'),
            ('class:prompt', ': ')
        ]), default="", style=style)
    if args.llm == "":
        args.llm = "anthropic"

    main(args.dir_path, args.output_file, args.prompt, args.doc_type, args.llm, args.ignore_dirs)

