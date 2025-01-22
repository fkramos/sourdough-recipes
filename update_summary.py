#!/usr/bin/env python3

import os
import re
import subprocess
from typing import Tuple, List

SRC_PATH = "src"
SUMMARY_FILE = os.path.join(SRC_PATH, "SUMMARY.md")

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
            if line.startswith("#"):  # Exemplo: '# Meu Título'
                # Remove todos os '#' e espaços para pegar só o título limpo.
                title = re.sub(r"^#+\s*", "", line)
                break
    return title

def get_file_creation_timestamp(file_path: str) -> int:
    """
    Retorna, em Unix timestamp (segundos), a data do primeiro commit que adicionou o arquivo.
    Caso não seja encontrado, retorna 0.
    """
    # Este comando filtra commits que adicionaram (A) o arquivo
    # e formata a data em segundos (Unix epoch).
    # O 'head -1' vai pegar o commit mais antigo (o primeiro) que adicionou o arquivo.
    cmd = [
        "git", "log", "--diff-filter=A", "--follow", 
        "--format=%at",  # apenas o timestamp
        file_path
    ]
    try:
        # Captura a saída do git log
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Pega a primeira linha (primeira data), se existir
        lines = result.stdout.strip().splitlines()
        if lines:
            return int(lines[-1])  # se quiser pegar o mais antigo, use lines[-1] ou lines[0], dependendo da ordem
        else:
            return 0
    except subprocess.CalledProcessError:
        return 0

def main():
    # Coletar arquivos MD em src, exceto os da lista de exclusão
    md_files = []
    for entry in os.scandir(SRC_PATH):
        if entry.is_file() and entry.name.endswith(".md") and entry.name not in EXCLUDED_FILES:
            md_files.append(entry.path)

    # Obter timestamp do primeiro commit de cada arquivo e ordenar
    # Quanto maior o timestamp, mais recente. Se você quiser do mais antigo para o mais recente,
    # altere a lógica conforme desejar.
    # Neste exemplo, ordenamos do mais antigo (menor timestamp) para o mais novo (maior timestamp).
    file_with_dates = []
    for fpath in md_files:
        timestamp = get_file_creation_timestamp(fpath)
        file_with_dates.append((fpath, timestamp))

    # Ordena pelos timestamps (do menor para o maior)
    file_with_dates.sort(key=lambda x: x[1])

    # Monta as linhas para o SUMMARY.md
    lines = [
        "# Sumário\n",
        "\n",
        "* [Início](README.md)\n",
    ]

    for fpath, _timestamp in file_with_dates:
        title = extract_title_from_md(fpath)
        filename = os.path.basename(fpath)
        lines.append(f"* [{title}]({filename})\n")

    # Escreve o novo SUMMARY.md
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

if __name__ == "__main__":
    main()
