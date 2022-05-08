Functions and Methods
---------------------

`kernels`
while ensuring the interface will always remain the same,
even across different plugins with their own settings and expected behavior.

For example, if you want to downscale a video clip to 1280x720 using Bicubic (b=0, c=1),
you can call the preset, :py:class:`vskernels.kernels.SharpBicubic`, like so:

.. code-block:: py

    kernels.SharpBicubic().scale(clip, width=1280, height=720)

Of course, there is also a generic Bicubic class should you want to assign the values manually.

.. code-block:: py

    kernels.Bicubic(b=0, c=1).scale(clip, width=1280, height=720)

This allows for easy customizability, and every kernel can be given unique parameters if required.

.. code-block:: py

    kernels.Bicubic(b=0, c=0.5)
    kernels.Lanczos(taps=3)
    kernels.Impulse(impulse, oversample=8, taps=1)

Using this interface allows for consistency, which makes supporting a wide array of kernels in your own function very simple.

Supporting Kernels in Your Own Function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autosummary::

    vskernels.kernels.get_kernel
    vskernels.kernels.get_all_kernels

Kernels are very flexible, so if you want to use them as-is, they're simple enough to add. However, you should also consider newer users and their inexperience with Kernels, but potential exposure to abusing strings for "presets".

With that in mind, we believe the most optimal method to implement kernels is by allowing your function to accept both a `Kernel` object and a string. This allows users who want to make full use of kernels to do so while not making it any harder for newer users to rely on strings.

Below is some example code for implementing kernel support into a simple descaling function:

.. code-block:: py

    from vskernels import Kernel, get_kernel

    def descale(clip: vs.VideoNode,
                width: int = 1280, height: int = 720,
                kernel: Kernel | str = 'bicubic') -> vs.VideoNode:
        """A simple descaling function"""

        if isinstance(kernel, str):
            kernel = get_kernel(kernel)()

        descaled_clip = kernel.descale(clip, width, height)
        return descaled_clip

Which in turn allows users to call the function in multiple ways:

.. code-block:: py

    import vskernels as kernels

    example1 = descale(clip, 1280, 720, kernels.Bicubic())
    example2 = descale(clip, 1280, 720, 'bicubic')

Easy as pie!

Functions
^^^^^^^^^

.. autoclass:: vskernels.kernels.get_kernel
    :members:

.. autoclass:: vskernels.kernels.get_all_kernels
    :members:

Methods
^^^^^^^

Every `Kernel` class comes with a set of methods:

.. autoclass:: vskernels.kernels.Example.scale
    :members:

.. autoclass:: vskernels.kernels.Example.descale
    :members:

.. autoclass:: vskernels.kernels.Example.shift
    :members:

.. autoclass:: vskernels.kernels.Example.resample
    :members:

All Available Kernels
^^^^^^^^^^^^^^^^^^^^^

.. automodule:: vskernels.kernels
    :members:
    :show-inheritance:
    :exclude-members: Example, get_kernel, get_all_kernels
