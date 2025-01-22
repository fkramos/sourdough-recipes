import os
import re

def generate_summary(src_dir):
    summary = "# Summary\n\n"
    
    # Ignorar o próprio SUMMARY.md
    exclude_files = {'SUMMARY.md'}
    
    for root, dirs, files in os.walk(src_dir):
        # Ordena diretórios e arquivos
        dirs.sort()
        files.sort()
        
        # Calcula o nível de indentação baseado na profundidade do diretório
        level = root[len(src_dir):].count(os.sep)
        indent = '    ' * level
        
        # Adiciona os arquivos markdown do diretório atual
        for file in files:
            if file.endswith('.md') and file not in exclude_files:
                # Lê o título do arquivo MD (primeira linha # Título)
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                    title = title_match.group(1) if title_match else file[:-3]
                
                # Cria o caminho relativo
                rel_path = os.path.relpath(file_path, src_dir)
                summary += f'{indent}- [{title}]({rel_path})\n'
    
    return summary

def update_summary(src_dir):
    summary_content = generate_summary(src_dir)
    summary_path = os.path.join(src_dir, 'SUMMARY.md')
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)

if __name__ == "__main__":
    src_dir = "./src"  # Ajuste para o caminho da sua pasta src
    update_summary(src_dir)
