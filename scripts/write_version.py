import json, pathlib


pkg = pathlib.Path('ipycanvas')
pkg.mkdir(exist_ok=True)

with open('package.json') as f:
    version = json.load(f)['version']

with open(pkg / '_version.py', 'w') as f:
    f.write(
        '# Auto-generated from package.json\n'
        '\n'
        f'__version__ = "{version}"\n'
    )
