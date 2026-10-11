#!/usr/bin/env python3
import re
import json
import ollama
import pyperclip
import sys
import argparse
from collections import defaultdict

class Colors:
    INSTRUCTION = '\033[96m'  # Cyan
    INPUT = '\033[93m'        # Yellow
    OUTPUT = '\033[92m'       # Green
    MAPPING = '\033[95m'      # Magenta
    ERROR = '\033[91m'        # Red
    BOLD = '\033[1m'
    RESET = '\033[0m'

class Tokeniser:
    def __init__(self):
        self.mapping = {}
        self.counter = defaultdict(lambda: 1) 

    def clear(self):
        self.mapping = {}
        self.counter = defaultdict(lambda: 1)

    def _get_token(self, entity, category):
        category = str(category).upper().replace(" ", "_")
        
        for token, original in self.mapping.items():
            if original == entity:
                return token

        count = self.counter[category]
        token = f"[{category}_{count}]"
        self.mapping[token] = entity
        self.counter[category] += 1
            
        return token

    def extract_entities_with_local_llm(self, text):
        prompt = (
            "Analyse the following text and identify all private, sensitive, or personally identifiable information (PII) "
            "such as names of people, companies, organisations, or other private entities. "
            "Return the result strictly as a JSON array of objects. Each object must have two keys: "
            "\"entity\" (the exact substring from the text) and \"category\" (a short, uppercase category name like PERSON, ORGANISATION, or LOCATION). "
            f"\n\nText: {text}"
        )
        
        try:
            response = ollama.chat(
                model='llama3',
                messages=[{'role': 'user', 'content': prompt}],
                format='json'
            )
            
            content = response.get('message', {}).get('content', '[]')
            return json.loads(content)
        except Exception as e:
            print(f"{Colors.ERROR}LLM extraction error: {e}{Colors.RESET}")
            return []

    def anonymise(self, text):
        entities = self.extract_entities_with_local_llm(text)
        
        if isinstance(entities, dict):
            for value in entities.values():
                if isinstance(value, list):
                    entities = value
                    break
        
        if isinstance(entities, list):
            for item in entities:
                if isinstance(item, dict):
                    entity = item.get("entity")
                    category = item.get("category", "PII")
                    if entity and entity in text:
                        token = self._get_token(entity, category)
                        text = text.replace(entity, token)

        text = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', lambda m: self._get_token(m.group(), 'IP_ADDRESS'), text)
        text = re.sub(r'[\w\.-]+@[\w\.-]+', lambda m: self._get_token(m.group(), 'EMAIL'), text)
        text = re.sub(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,63}\b', lambda m: self._get_token(m.group(), 'DOMAIN'), text)

        return text

    def deanonymise(self, text):
        for token, original in self.mapping.items():
            text = text.replace(token, original)
        return text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Token Ghost")
    parser.add_argument("-l", "--loop", action="store_true", help="Enable continuous loop mode to reuse tokens")
    parser.add_argument("-s", "--show-tokens", action="store_true", help="Show token mapping after generation")
    args = parser.parse_args()

    continuous_loop = args.loop
    show_tokens = args.show_tokens

    print(f"{Colors.BOLD}{Colors.INSTRUCTION}--- Token Ghost ---{Colors.RESET}\n")
    
    tokeniser = Tokeniser()

    while True:
        print(f"{Colors.INSTRUCTION}Enter the raw input to anonymise. Type '.' on a new line when finished (or 'EXIT' to quit, 'r' to reset tokens):{Colors.RESET}")
        print(Colors.INPUT, end="", flush=True)
        
        raw_lines = []
        while True:
            try:
                line = input()
                if line.strip() == ".":
                    break
                if line.strip().upper() == "EXIT" and not raw_lines:
                    sys.exit(0)
                if line.strip().lower() == "r" and not raw_lines:
                    tokeniser.clear()
                    print(f"\n{Colors.OUTPUT}--- Tokens cleared ---{Colors.RESET}\n")
                    print(f"{Colors.INSTRUCTION}Enter the raw input to anonymise. Type '.' on a new line when finished (or 'EXIT' to quit, 'r' to reset tokens):{Colors.RESET}")
                    print(Colors.INPUT, end="", flush=True)
                    continue
                raw_lines.append(line)
            except EOFError:
                break
                
        print(Colors.RESET, end="", flush=True)
        input_text = "\n".join(raw_lines)
        
        if not input_text.strip():
            print(f"{Colors.ERROR}No input provided. Please try again.{Colors.RESET}\n")
            continue
            
        print(f"\n{Colors.INSTRUCTION}Processing with local LLM...{Colors.RESET}\n")
        safe_text = tokeniser.anonymise(input_text)
        
        if show_tokens and tokeniser.mapping:
            print(f"{Colors.BOLD}{Colors.MAPPING}--- Current Token Mapping ---")
            for token, original in tokeniser.mapping.items():
                print(f"{token}: {original}")
            print(f"-----------------------------{Colors.RESET}\n")
        
        try:
            pyperclip.copy(safe_text)
            clipboard_status = "(copied to clipboard)"
        except Exception:
            clipboard_status = "(could not copy to clipboard)"
            
        print(f"{Colors.BOLD}{Colors.OUTPUT}Tokenised output {clipboard_status}:{Colors.RESET}\n")
        print(f"{Colors.OUTPUT}{safe_text}{Colors.RESET}")
        print(f"\n{Colors.INSTRUCTION}========================================{Colors.RESET}\n")

        print(f"{Colors.INSTRUCTION}Paste the response from the external AI. Type '.' on a new line when finished:{Colors.RESET}")
        print(Colors.INPUT, end="", flush=True)
        
        external_lines = []
        while True:
            try:
                line = input()
                if line.strip() == ".":
                    break
                external_lines.append(line)
            except EOFError:
                break
                
        print(Colors.RESET, end="", flush=True)
        external_response = "\n".join(external_lines)
        
        if external_response.strip():
            restored_response = tokeniser.deanonymise(external_response)
            print(f"\n{Colors.BOLD}{Colors.OUTPUT}Restored output:{Colors.RESET}\n")
            print(f"{Colors.OUTPUT}{restored_response}{Colors.RESET}")

            try:
                pyperclip.copy(restored_response)
                print(f"\n{Colors.INSTRUCTION}(Restored output copied to clipboard){Colors.RESET}\n")
            except Exception:
                print(f"\n{Colors.ERROR}(Could not copy restored output to clipboard){Colors.RESET}\n")
                
        if not continuous_loop:
            break
        else:
            print(f"{Colors.INSTRUCTION}--- Ready for next input (tokens preserved) ---{Colors.RESET}\n")