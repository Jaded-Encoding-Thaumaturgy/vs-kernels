Basic Usage
-----------


Importing
^^^^^^^^^

`vs-kernels` is a Python module,
meaning it must be imported into your script before it can be accessed.
You can import it by doing the following:

.. code-block:: py

    import vskernels as kernels

With the module now imported,
you can call functions in your script by referencing the module
and writing a function name behind it.

.. code-block:: py

    import vskernels as kernels

    kernels.get_kernel()
    upscale = kernels.Catrom().scale(clip, 1920, 1080)


Scaling
^^^^^^^

With kernels, you can do a lot of scaling and conversion all from one function.
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


Format Conversion
^^^^^^^^^^^^^^^^^

Another common conversion is a *format conversion*.
A couple plugins require you to pass an RGB clip, for example.
With kernels, it's easy to convert on the spot using a sane kernel to do the job.

.. code-block:: py

    import vskernels as kernels

    to_rgb = kernels.Bicubic().resample(clip, vs.RGBS, matrix_in=1)

    back_to_yuv = kernels.Bicubic().resample(to_rgb, vs.YUV, matrix=1)
