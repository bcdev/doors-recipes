from  glob import glob
import subprocess

md_files = glob('*.md')

for md_file in md_files:
    doc_file = f'{md_file.split(".md")[0]}.docx'
    subprocess.run(['pandoc', '-o', f'{doc_file}', '-f', 'markdown', '-t',
                    'docx', f'{md_file}'])
