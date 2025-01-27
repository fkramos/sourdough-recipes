#!/usr/bin/env python3

import os
import re
import subprocess
from typing import Dict, List, Tuple

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
    Caso não encontre, retorna 0.

    Observação importante:
    - 'git log' lista commits do mais recente para o mais antigo.
    - Portanto, lines[0] é o commit mais novo, lines[-1] é o mais antigo.
    - Se queremos a data de criação (commit mais antigo), retornamos lines[-1].
    """
    cmd = [
        "git", "log", "--diff-filter=A", "--follow",
        "--format=%at",  # apenas o timestamp Unix
        file_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().splitlines()
        if lines:
            # lines[-1] => commit mais antigo (criador do arquivo).
            return int(lines[-1])
        else:
            return 0
    except subprocess.CalledProcessError:
        return 0

def main():
    """
    Faz varredura recursiva em 'src/', agrupa por subpastas, e gera o SUMMARY.md
    em formato de seções, ordenando os arquivos do mais antigo (topo) para o mais recente (fundo).
    """
    subfolders_map: Dict[str, List[Tuple[int, str, str]]] = {}

    for root, dirs, files in os.walk(SRC_PATH):
        for file_name in files:
            if not file_name.endswith(".md"):
                continue
            if file_name in EXCLUDED_FILES:
                continue

            file_path = os.path.join(root, file_name)
            timestamp = get_file_creation_timestamp(file_path)
            title = extract_title_from_md(file_path)

            # Subpasta relativa em relação a src/
            rel_path = os.path.relpath(root, SRC_PATH)
            if rel_path == ".":
                rel_path = ""

            # Armazena (timestamp, caminho, título) no dicionário da subpasta
            if rel_path not in subfolders_map:
                subfolders_map[rel_path] = []
            subfolders_map[rel_path].append((timestamp, file_path, title))

    # Inicia o conteúdo do SUMMARY.md
    lines = [
        "# Sumário\n",
        "\n",
        "* [Início](README.md)\n",
    ]

    # Ordena as subpastas pelo nome (alfabético) apenas para uma ordem previsível de seções
    subfolders_sorted = sorted(subfolders_map.keys())

    for subfolder in subfolders_sorted:
        # Aqui fazemos a ordenação pelo timestamp em ordem ASCENDENTE (mais antigo primeiro).
        subfolders_map[subfolder].sort(key=lambda x: x[0])  # sem reverse

        # Se for subpasta vazia, significa que está no próprio SRC
        if subfolder:
            folder_title = subfolder.replace("-", " ").title()
            lines.append(f"\n## {folder_title}\n\n")

        for timestamp, fpath, title in subfolders_map[subfolder]:
            file_rel_to_src = os.path.relpath(fpath, SRC_PATH)
            lines.append(f"* [{title}]({file_rel_to_src})\n")

    # Salva o arquivo
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

if __name__ == "__main__":
    main()
