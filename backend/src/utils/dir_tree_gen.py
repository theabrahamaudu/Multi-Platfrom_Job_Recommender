# Importing Libraries
import sys
import os
from directory_tree import display_tree


def main(dir: str = ''):
    if dir == '':
        # get the current working directory
        path = os.getcwd()
    else:
        # join the path with the current working directory
        path = os.path.join(os.getcwd(), dir)
    structure = display_tree(
        dir_path=path,
        max_depth=5,
        string_rep=True,
        ignore_list=[
            '.ipynb_checkpoints',
            '.venv',
            '.git*',
            '__pycache__',
            '__init__.py',
            'sentence-transformers',
            'server.htpasswd',
            'cassandra/data'
        ]
    )
    os.chdir(path)
    # save the markdown file
    if len(dir) == 0:
        file_name = 'dir_tree.md'
    else:
        file_name = f'dir_tree_{dir}.md'
    with open(file_name, 'w') as f:
        f.write(f"""{structure}""")
    print(f"Markdown file '{file_name}' created successfully.")


# Main Method
if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
