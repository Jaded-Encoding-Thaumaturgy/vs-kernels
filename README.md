# vs-kernels

<p align="center">
    <a href="https://vs-kernels.encode.moe"><img alt="Read the Docs" src="https://img.shields.io/readthedocs/vs-kernels"></a>
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/vs-kernels">
    <a href="https://pypi.org/project/vs-kernels/"><img alt="PyPI" src="https://img.shields.io/pypi/v/vs-kernels"></a>
    <a href="https://github.com/Irrational-Encoding-Wizardry/vs-kernels/commits/master"><img alt="GitHub commits since tagged version" src="https://img.shields.io/github/commits-since/Irrational-Encoding-Wizardry/vs-kernels/latest"></a>
    <a href="https://github.com/Irrational-Encoding-Wizardry/vs-kernels/blob/master/LICENSE"><img alt="PyPI - License" src="https://img.shields.io/pypi/l/vs-kernels"></a>
    <a href="https://discord.gg/qxTxVJGtst"><img alt="Discord" src="https://img.shields.io/discord/856381934052704266?label=discord"></a>
</p>

Kernels are a collection of wrappers pertaining to (de)scaling, format conversion,
and other related operations, all while providing a consistent and clean interface.
This allows for easy expansion and ease of use for any other maintainers
who wishes to use them in their own functions.

You can create presets for common scaling algorithms or settings,
while ensuring the interface will always remain the same,
even across different plugins with their own settings and expected behavior.

Full information on how every function/wrapper works,
as well as a list of dependencies and links,
can be found in the [documentation](https://vs-kernels.encode.moe/en/latest/).
For further support,
drop by `#kernels` in the [IEW Discord server](https://discord.gg/qxTxVJGtst).

## How to install

Install `vs-kernels` with the following command:

```sh
$ pip3 install vskernels --no-cache-dir -U
```

Or if you want the latest git version, install it with this command:

```sh
$ pip3 install git+https://github.com/Irrational-Encoding-Wizardry/vs-kernels.git --no-cache-dir -U
```
