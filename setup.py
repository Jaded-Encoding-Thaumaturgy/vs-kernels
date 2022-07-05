#!/usr/bin/env python3

import setuptools
from pathlib import Path
from typing import cast, Dict

package_name = 'vskernels'

exec(Path(f'{package_name}/_metadata.py').read_text(), meta := cast(Dict[str, str], {}))

readme = Path('README.md').read_text()
requirements = Path('requirements.txt').read_text()


setuptools.setup(
    name=package_name,
    version=meta['__version__'],
    author=meta['__author_name__'],
    author_email=meta['__author_email__'],
    maintainer=meta['__maintainer_name__'],
    maintainer_email=meta['__maintainer_email__'],
    description=meta['__doc__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    project_urls={
        'Source Code': 'https://github.com/Irrational-Encoding-Wizardry/vs-kernels',
        'Documentation': 'https://vskernels.encode.moe/en/latest/',
        'Contact': 'https://discord.gg/qxTxVJGtst',
    },
    install_requires=requirements,
    python_requires='>=3.8',
    packages=[
        package_name
    ],
    package_data={
        package_name: ['py.typed']
    },
    classifiers=[
        "Natural Language :: English",

        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",

        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Typing :: Typed",

        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Display",
    ],
    command_options={
        "build_sphinx": {
            "project": ("setup.py", package_name),
            "version": ("setup.py", meta['__version__']),
            "release": ("setup.py", meta['__version__']),
            "source_dir": ("setup.py", "docs")
        }
    }
)
