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
    """
    cmd = [
        "git", "log", "--diff-filter=A", "--follow", 
        "--format=%at",  # apenas o timestamp Unix
        file_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().splitlines()
        # Se o git não retornar nada, quer dizer que não encontrou commits
        if lines:
            # Por padrão, git log ordena do mais recente pro mais antigo.
            # Então o primeiro da lista ("lines[0]") é o mais recente,
            # e o último da lista ("lines[-1]") é o mais antigo.
            # Para pegar a data mais antiga (ou seja, quando o arquivo
            # foi introduzido pela primeira vez), use "lines[-1]".
            return int(lines[-1])
        else:
            return 0
    except subprocess.CalledProcessError:
        return 0

def main():
    """
    Faz varredura recursiva em 'src/', agrupa por subpastas, e gera o SUMMARY.md
    em formato de seções, ordenando os arquivos pelo timestamp de criação.
    """
    # Vamos mapear subpastas -> lista de arquivos
    # Cada item da lista será (timestamp, arquivo, título).
    subfolders_map: Dict[str, List[Tuple[int, str, str]]] = {}

    # Fazemos um "os.walk" para varrer recursivamente a partir de SRC_PATH
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
            rel_path = os.path.relpath(root, SRC_PATH)  # pode ser '.' se for o próprio src
            # Se rel_path for '.', quer dizer que o arquivo está diretamente em src,
            # fora de qualquer subpasta. Vamos usar algo como "root" = "" para armazenar.
            if rel_path == ".":
                rel_path = ""

            if rel_path not in subfolders_map:
                subfolders_map[rel_path] = []
            subfolders_map[rel_path].append((timestamp, file_path, title))

    # Agora geramos a estrutura do SUMMARY.md
    lines = [
        "# Sumário\n",
        "\n",
        "* [Início](README.md)\n",
    ]

    # Para exibir as subpastas em alguma ordem previsível, vamos ordenar
    # pelo nome da subpasta. Se quiser seguir outra lógica, mude aqui.
    subfolders_sorted = sorted(subfolders_map.keys())

    for subfolder in subfolders_sorted:
        # Ordena os arquivos desta subpasta pelo timestamp (mais antigo primeiro)
        subfolders_map[subfolder].sort(key=lambda x: x[0])

        # Se subfolder for vazio, quer dizer que está na raiz do SRC.
        # Podemos criar uma sessão só se não for vazio, caso deseje ignorar a raiz.
        if subfolder:
            # Aqui podemos formatar um título para a seção (ex: "pao-frances" -> "Pao Frances")
            # ou usar o nome da pasta cru. Para um "titulo" rápido:
            folder_title = subfolder.replace("-", " ").title()  # Exemplo: "pao-frances" -> "Pao Frances"
            lines.append(f"\n## {folder_title}\n\n")

        for timestamp, fpath, title in subfolders_map[subfolder]:
            # Precisamos do caminho relativo a src/ para criar o link.
            # file_rel_to_src, pois fpath é o caminho absoluto no repositório
            file_rel_to_src = os.path.relpath(fpath, SRC_PATH)
            lines.append(f"* [{title}]({file_rel_to_src})\n")

    # Escreve o novo SUMMARY.md
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

if __name__ == "__main__":
    main()
