import os
import re

SOURCE = './source'
EXT = '.rst'

TARGET = re.compile('(Subpackages|Submodules|-+?)\n')


for rst_path in [os.path.join(SOURCE, path) for path in os.listdir(SOURCE) if path.endswith(EXT)]:
    rst_out = ""

    with open(rst_path, 'r') as rst_file:
        for line in rst_file:
            if not re.match(TARGET, line):
                rst_out += line
            else:
                found = True

    with open(rst_path, 'w') as rst_file:
        rst_file.write(rst_out)

