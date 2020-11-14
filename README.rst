parspace
========

This module is a simple tool to automatically explore a parameter space.

You can install parspace with ``pip``::

    $ python3 -m pip install -U --user parspace

It provides a class that can be used to aumatically run a function over
all possible combinations of a given parameter space.

Say that you have a problem controlled by two parameters: an aspect ratio
``asp`` and a density ``density``.  The following example shows how to use
``ParSpace`` to automatically explore every combination of the requested values
for these two parameters.  If you have a function (here called ``launch_simu``)
that performs the desired simulation for a given value of these two parameters,
you merely have to use ``ParSpace`` as a decorator on that function.

.. code:: python

    from parspace import ParSpace


    @ParSpace(asp=[0.5, 1, 2],
              density=[1, 10])
    def launch_simu(asp, density):
        print(f"aspect ratio {asp} and density {density}")


    launch_simu()

This code will print the following on screen::

    aspect ratio 0.5 and density 1
    aspect ratio 0.5 and density 10
    aspect ratio 1 and density 1
    aspect ratio 1 and density 10
    aspect ratio 2 and density 1
    aspect ratio 2 and density 10

In real use cases, ``launch_simu`` could e.g. perform the desired simulation or
submit a job on a supercomputer.  Note that the order of arguments of
``launch_simu`` does not matter, only their names.  In other words, if you
define it as ``def launch_simu(density, asp)``, you would obtain the same
result. On the other hand, defining it as ``def launch_simu(aspect, density)``
would result in a `TypeError` as the ``asp`` fed to ``ParSpace`` does not match
any argument of ``launch_simu``.

Note that if you have a large number of parameters, you might prefer declare
``launch_simu`` as taking a dictionary of keywords arguments.  Parameter names
and values would then be the keys and values of that dictionary.

.. code:: python

    from parspace import ParSpace


    @ParSpace(asp=[0.5, 1, 2],
              density=[1, 10])
    def launch_simu(**pars):
        print("aspect ratio {asp} and density {density}".format(**pars))


    launch_simu()