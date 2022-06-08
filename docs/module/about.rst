About Kernels
-------------

It's not uncommon for VapourSynth users and developers to require multiple scaling or format conversion libraries
in order to have access to every common convolution or formats.
`kernels` help solve this age-old problem by uniting multiple of these libraries under a single interface.
This allows for developers to support many libraries at once
without having to worry about implementing all of them themselves;
vs-kernels handles that for you.

Kernels are fairly extensive.
For example, say you want to downscale a video clip to 1280x720 using *bicubic*.
You can call it directly like so:

.. code-block:: py

    kernels.Bicubic().scale(clip, width=1280, height=720)

But what if you want to use specific parameters?
Say you want to use `b=0, c=1`, commonly known as Sharp Bicubic.
Changing the Bicubic settings can easily be done through the Kernel object's parameters.

.. code-block:: py

    kernels.Bicubic(b=0, c=1).scale(clip, width=1280, height=720)

Or you can use the preset, :py:class:`vskernels.kernels.BicubicSharp`,
to quickly call the exact common variant of Bicubic you want.

.. code-block:: py

    kernels.BicubicSharp().scale(clip, width=1280, height=720)


This allows for easy customizability, and every kernel can be given unique parameters if required.

.. code-block:: py

    kernels.Bicubic(b=0.2, c=0.4)
    kernels.Lanczos(taps=3)
    kernels.Impulse(impulse, oversample=8, taps=1)

Using this interface allows for consistency,
which makes supporting a wide array of kernels in your own function very simple.
