# Token Ghost

Token Ghost is a local Python CLI tool designed to anonymise sensitive data before passing it to external AI services. It uses a local LLM via Ollama to dynamically identify personally identifiable information (PII)/personal data alongside regular expressions for structured data.

## Features

* **100% Offline Extraction:** Uses Ollama and Llama 3 to ensure your raw data never leaves your machine.

* **Dynamic Categorisation:** Automatically detects and categorises names, organisations, and locations.

* **Structured Data Masking:** Uses fast regular expressions to catch IP addresses, emails, and domains.

* **Clipboard Integration:** Automatically copies obfuscated and restored text to your clipboard.

* **Persistent Tokens:** Optional loop mode keeps your token mappings alive for continuous conversations.

## Prerequisites

* Python 3

* [Ollama](https://ollama.com/) installed with the `llama3` model

* System clipboard utility (such as `xclip` or `xsel` on Linux)

## Installation

1. Clone the repository:

```bash
git clone --depth=1 https://github.com/rbrown256/token-ghost.git
cd token-ghost
```

2. Install Ollama and download the Llama 3 model:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
```

3. Install the required Python libraries:

```bash
pip3 install ollama pyperclip
```

4. Make the script executable:

```bash
chmod +x token-ghost.py
```

## Usage

Run the script directly from your terminal:

```bash
python3 token-ghost.py
```

### Command Line Options

* `-l`, `--loop`: Enable continuous loop mode to reuse tokens across multiple inputs.

* `-s`, `--show-tokens`: Display the token mapping table after generation.

### Interactive Commands

* Type your text and press Enter.

* Type `.` on a new blank line to submit your input.

* Type `r` on a new blank line to reset all current token mappings.

* Type `EXIT` on a new blank line to quit the application.

## How It Works

1. **Input:** You paste raw text containing private data into Token Ghost.

2. **Tokenisation:** The tool scans the text and replaces entities with tags like `[PERSON_1]` or `[EMAIL_1]`, then copies the safe text to your clipboard.

3. **External AI:** You paste the tokenised text into your external AI of choice.

4. **Restoration:** You copy the AI's response, paste it back into Token Ghost, and it replaces the tokens with your original private data.

## ⚠️ Important Security Warning

**Do not blindly copy and paste the output.** 

While Token Ghost uses local LLMs and regular expressions to identify sensitive information, no automated system is completely infallible. Generative models can occasionally miss edge cases, fail to recognise obscure entities, or misinterpret context. 

* **Always double check** the tokenised output manually to verify that all private data has been successfully masked before pasting it into any external AI or third party service.
* You are solely responsible for verifying the sanitised text. 
* The author of this tool accepts zero liability for any data leaks, privacy breaches, or unintentional sharing of sensitive information that occurs as a result of using this software. Use this tool entirely at your own risk.