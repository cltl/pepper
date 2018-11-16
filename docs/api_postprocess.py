import os
import re

SOURCE = './source'
EXT = '.rst'

TARGET = re.compile('(Subpackages|Submodules)\n-+?\n')

for rst_path in [os.path.join(SOURCE, path) for path in os.listdir(SOURCE) if path.endswith(EXT)]:
    with open(rst_path, 'r') as rst_file:
        rst = re.sub(TARGET, '', rst_file.read())
    with open(rst_path, 'w') as rst_file:
        rst_file.write(rst)

