#!/usr/bin/env python3

from pathlib import Path
from typing import cast

import setuptools

package_name = 'vskernels'

exec(Path(f'{package_name}/_metadata.py').read_text(), meta := cast(dict[str, str], {}))

readme = Path('README.md').read_text()
requirements = Path('requirements.txt').read_text()

# stubs comand
# vsgenstubs4 std resize descale fmtc placebo -o stubs


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
        'Source Code': 'https://github.com/Jaded-Encoding-Thaumaturgy/vs-kernels',
        'Contact': 'https://discord.gg/XTpc6Fa9eB',
    },
    install_requires=requirements,
    python_requires='>=3.11',
    packages=[
        package_name, f'{package_name}.kernels'
    ],
    package_data={
        package_name: ['py.typed']
    },
    classifiers=[
        "Natural Language :: English",

        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",

        "Programming Language :: Python :: 3.10",
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
