# Repo2Docs: Convert Repositories to Documentation

Inspired by [github2file](https://github.com/cognitivecomputations/github2file)

Repo2Docs is a Python-based tool designed to convert the contents of a repository into comprehensive documentation or diagrams. This tool leverages language model APIs such as OpenAI or Anthropic to process and generate documentation, making it easier for developers to create documentation for their projects.

## Usage

To run Repo2Docs on your local machine, follow these steps:

1. **Install Repo2Docs**:
   ```
   pip install repo2docs
   ```


2. **Set Up Environment Variables**:
   Export your OpenAI and Anthropic API keys as environment variables:
   ```
   export OPENAI_API_KEY=your_openai_api_key_here
   export ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```
   or
   Input your OpenAI or Anthropic API keys when prompted


3. **Run the Tool**:

   Navigate to the directory containing the repository:
   ```
   cd <path_to_repo>
   ```
   To start Repo2Docs with an interactive prompt, execute:
   ```
   repo2docs
   ```
   Alternatively, you can specify options directly via command-line flags:
   ```
   repo2docs --dir_path . --output_file README.md --type documentation --llm openai
   ```

   - `dir_path`: Specifies the directory of the repo. If omitted, defaults to the current directory.
   - `output_file`: Sets the name and path of the output file. If omitted, defaults to `README.md`.
   - `type`: Determines the type of output generated. Options include:
     - `documentation` (default)
     - `diagram` for visual diagrams
     - `database` for database ERD diagrams
     - Custom prompt: Leave `type` unspecified and use `--prompt "<prompt>"` to provide a custom prompt.
   - `llm`: Selects the language model to use. If omitted, defaults to `openai`. Options include:
     - `openai` (default model: `gpt-4-turbo`)
     - `anthropic` (default model: `claude-3-haiku-20240307`)
   - `model`: Specifies the model to use for generating documentation. If omitted, defaults to the default model for the selected language model.

## Supported File Types

Repo2Docs currently supports processing files with the following extensions: `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.c`, `.cpp`, `.h`, `.hpp`. It filters out files from directories like `docs`, `examples`, `tests`, and others that are unlikely to contain useful information for documentation.

## Contributing

Contributions to Repo2Docs are welcome! Whether it's adding new features, improving documentation, or reporting issues, feel free to open an issue or submit a pull request.

## License

Repo2Docs is released under the MIT License. See the LICENSE file for more details.



