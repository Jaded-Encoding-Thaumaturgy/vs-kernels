Adding Kernels to Your Module
-----------------------------

The best way to add support to your module
is to first ensure you create a `proper package <https://realpython.com/pypi-publish-python-package/>`_.
This will force your users to install all the dependencies you set.
In your `requirements.txt`, simply add the following line:

.. code-block:: rst

    vskernels>=1.0.4

You can then easily import vs-kernels as you would normally
without having to worry whether your users have vs-kernels installed.

In case you don't have a package or don't want to create one,
the easiest way to is to either import it and catch it in a try/except,
or to have a list of required dependencies with links in your README.

An example of catching an import exception:

.. code-block:: py

    try:
        from vskernels import Kernel, get_kernel
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "Could not import vs-kernels! Please download it here: ""https://github.com/Jaded-Encoding-Thaumaturgy/vs-kernels"
        )

This will prompt the user to install vs-kernels
if they don't have it already.
