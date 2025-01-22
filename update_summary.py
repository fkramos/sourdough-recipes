#!/usr/bin/env python3

import os
import re

# Caminho relativo para a pasta que contém os arquivos MD.
SRC_PATH = "src"
SUMMARY_FILE = os.path.join(SRC_PATH, "SUMMARY.md")

# Quais arquivos devem ser ignorados. 
# Você pode adicionar ou remover itens da lista conforme necessidade.
EXCLUDED_FILES = ["README.md", "SUMMARY.md"]

def extract_title_from_md(file_path: str) -> str:
    """
    Extrai o título de um arquivo Markdown pela primeira linha que inicia com '#'.
    Se não encontrar, usa o nome do arquivo (sem extensão) como título.
    """
    title = os.path.splitext(os.path.basename(file_path))[0]
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):  # Ex: '# Meu Título'
                # Remove todos os '#' e espaços extras para pegar só o título limpo.
                title = re.sub(r"^#+\s*", "", line)
                break
    return title

def main():
    # 1. Coletar todos os arquivos MD em src, exceto aqueles em EXCLUDED_FILES.
    md_files = []
    for entry in os.scandir(SRC_PATH):
        if entry.is_file() and entry.name.endswith(".md") and entry.name not in EXCLUDED_FILES:
            md_files.append(entry.path)

    # 2. Ordenar alfabeticamente, se desejar, ou deixar na ordem de criação.
    md_files.sort()

    # 3. Extrair títulos e construir conteúdo do SUMMARY.md.
    lines = [
        "# Sumário\n",
        "\n",
        "[Início](README.md)\n",
    ]
    for md_file in md_files:
        title = extract_title_from_md(md_file)
        filename = os.path.basename(md_file)
        lines.append(f"* [{title}]({filename})\n")

    # 4. Escrever o arquivo SUMMARY.md.
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

if __name__ == "__main__":
    main()
