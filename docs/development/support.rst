Kernels a Function
------------------

Kernels are very flexible, making it easy to implement in your own functions and methods.

For example, let's create a simple descaling function that allows users to pass their own scaling options.
A common descaling function will most likely have a signature not unlike this:

.. code-block:: py

    def descale(clip: vs.VideoNode, kernel: str = 'bicubic',
                width: int = 1280, height: int = 720,
                b: float = 1/3, c: float = 1/3, taps: 3) -> vs.VideoNode:
        if kernel is 'bicubic':
            return core.descale.Debicubic(clip, width, height, b=b, c=c)
        elif kernel is 'bilinear':
            return core.descale.Debilinear(clip, width, height)
        elif kernel is 'lanczos':
            return core.descale.Delanczos(clip, width, height, taps=taps)
        elif kernel is 'spline16':
            return core.descale.Despline16(clip, width, height)
        elif kernel is 'spline36':
            return core.descale.Despline36(clip, width, height)
        else:
            raise ValueError("Invalid kernel passed")


But this is very bulky.
You end up with a lot of parameters that are kinda pointless,
making it harder to sift through for your average user.
This especially becomes a problem once you start building significantly bigger functions.
Doubly so if you want to start supporting kernels outside of the regular `descale` library,
like for example :py:class:`vskernels.kernels.Sinc`.
By the time you've written an elif for each, you'll be hundreds of lines of codes further,
and your function will quickly become an unmaintainable nightmare.
And let's not even get started on the more complex kernels like :py:class:`vskernels.kernels.Robidoux`!

.. autosummary::

    vskernels.kernels.get_kernel
    vskernels.kernels.get_all_kernels

Kernels simplify this process,
and allows you to write significantly less code for better results and support.
All while still allowing power users to use the tools they need
to get the specific kernels they're looking for.

However, that doesn't mean we should neglect regular users.
It has been common for a very, very long time to use strings to select a kernel.
Fortunately, vskernels offers support for that as well through the use of :py:class:`vskernels.kernels.get_kernel`.
Allowing users to pass either a string or a `Kernel` object is simple enough,
and takes significantly less code than doing a big if/else chain.

Below is the previous example `descale` function,
but outfitted to use vskernels instead:

.. code-block:: py

    from vskernels import Kernel, get_kernel

    def descale(clip: vs.VideoNode,
                width: int = 1280, height: int = 720,
                kernel: Kernel | str = 'bicubic') -> vs.VideoNode:
        """A simple descaling function"""

        if isinstance(kernel, str):
            kernel = get_kernel(kernel)()

        return kernel.descale(clip, width, height)

This makes maintaining your function a lot easier,
and allows your users to use whatever kernel they please.

The following will return the same thing for regular users...

.. code-block:: py

    import your_example_module as yem

    example1 = yem.descale(clip, 1280, 720, 'bicubic')
    example2 = yem.descale(clip, 1280, 720, 'bicubicsharp')
    example3 = yem.descale(clip, 1280, 720, 'robidoux')
    example4 = yem.descale(clip, 1280, 720, 'cosine')
    example5 = yem.descale(clip, 1280, 720, 'sinc')

\...As for powerusers!

.. code-block:: py

    import your_example_module as yem
    import vskernels as kernels

    example1 = yem.descale(clip, 1280, 720, kernels.Bicubic())
    example2 = yem.descale(clip, 1280, 720, kernels.BicubicSharp())
    example3 = yem.descale(clip, 1280, 720, kernels.Robidoux())
    example4 = yem.descale(clip, 1280, 720, kernels.Cosine())
    example5 = yem.descale(clip, 1280, 720, kernels.Sinc())

But should powerusers want to be more specific, they can easily set their own settings by using `vskernels`:

.. code-block:: py

    import your_example_module as yem
    import vskernels as kernels

    example1 = yem.descale(clip, 1280, 720, kernels.Bicubic(b=0.2, c=0.45))
    example2 = yem.descale(clip, 1280, 720, kernels.Lanczos(taps=2))
    example3 = yem.descale(clip, 1280, 720, kernels.Bicubic(b=-0.5, c=0.25))
    example4 = yem.descale(clip, 1280, 720, kernels.Bicubic(b=0, c=2))

And you won't having to worry about supporting all these edgecases. Easy as py!
