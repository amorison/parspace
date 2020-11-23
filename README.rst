parspace
========

This module is a simple tool to automatically explore a parameter space.

You can install parspace with ``pip``::

    $ python3 -m pip install -U --user parspace

Usage as a decorator
--------------------

This package provides a class that can be used to aumatically run a function
over all possible combinations of a given parameter space.

Say that you have a problem controlled by two parameters: an aspect ratio
``asp`` and a density ``density``.  The following example shows how to use
``ParSpace`` to automatically explore every combination of the requested values
for these two parameters.  If you have a function (here called ``launch_simu``)
that performs the desired task for a given value of these two parameters, you
merely have to use ``ParSpace`` as a decorator on that function.

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
submit a job on a supercomputer.  The order of arguments of ``launch_simu``
does not matter, only their names.  In other words, if its signature is instead
``def launch_simu(density, asp)``, you would obtain the same result. On the
other hand, defining it as ``def launch_simu(aspect, density)`` would result in
a ``TypeError`` when calling the function as the ``asp`` argument fed to
``ParSpace`` does not match any argument of ``launch_simu``.

If you have a large number of parameters, you might prefer defining
``launch_simu`` as taking a dictionary of keyword arguments.  Parameter names
and values are then the keys and values of that dictionary.

.. code:: python

    from parspace import ParSpace


    @ParSpace(asp=[0.5, 1, 2],
              density=[1, 10])
    def launch_simu(**pars):
        asp = pars['asp']
        density = pars['density']
        print(f"aspect ratio {asp} and density {density}")


    launch_simu()


Iterating through returned values
---------------------------------

If you care about the returned values of the wrapped function rather than on
its side effects, you can iterate over the decorated object as shown below.

.. code:: python

    from parspace import ParSpace


    @ParSpace(asp=[0.5, 1, 2],
              density=[1, 10])
    def calc_mass(asp, density):
        return asp * density


    for pars, mass in calc_mass:
        asp = pars['asp']
        density = pars['density']
        print(f"Mass for aspect {asp} at density {density}: {mass}")


Note that iterating through a bare ``ParSpace`` instance yields the parameters
dictionary.

.. code:: python

    from parspace import ParSpace


    space = ParSpace(asp=[0.5, 1, 2],
                     density=[1, 10])
    for pars in space:
        print("aspect ratio {asp} and density {density}".format(**pars))


Exploring the same space on several functions
---------------------------------------------

Provided that the iterables used to build the ``ParSpace`` instance can be
iterated through any number of times (mind that generators can only be iterated
through *once*), you can use that instance on several functions as follow.

.. code:: python

    from parspace import ParSpace


    space = ParSpace(asp=[0.5, 1, 2],
                     density=[1, 10])


    @space
    def launch_simu(asp, density):
        print(f"aspect ratio {asp} and density {density}")


    launch_simu()


    for pars, mass in space(lambda asp, density: asp * density):
        asp = pars['asp']
        density = pars['density']
        print(f"Mass for aspect {asp} at density {density}: {mass}")


Realistic example of a script submitting jobs
---------------------------------------------

This script shows a simplistic but realistic example of what ``ParSpace``
enables you to do.  This script is written for a particular system and is
therefore unlikely to work for you as-is but adapting it to your use case
should be a fairly simple task.  The function ``submit_jobs`` defines what
should be done for one specific job and its decorated version automatically
explore the desired parameter space.

.. code:: python

    #!/usr/bin/env python3
    """Submit jobs on a PBS enabled cluster.

    This script is for demonstration purpose only and offers no guarantee, please
    adapt it to your use case.
    """
    from functools import lru_cache
    from pathlib import Path
    import json
    import subprocess
    import textwrap

    from parspace import ParSpace


    QSUB = '/usr/local/bin/qsub'
    BATCH = textwrap.dedent("""\
        #!/bin/bash
        #PBS -N jobname
        #PBS -l nodes=1:ppn=8
        #PBS -q queuename
        #PBS -j oe
        #PBS -V
        cd {work_dir}
        mpirun -np 8 /path/to/executable > out.log 2> err.log
        sync
        exit
        """)
    ROOT = Path().resolve(strict=True)


    # If you need to compute an entry parameter that depends only on a subset of
    # all the parameters you explore, you might want to cache its result if the
    # computation is expensive.  This isn't necessary in this simplistic case and
    # is only for illustrative purposes.
    @lru_cache(maxsize=None)
    def n_horiz(aspect_ratio):
        """Compute grid size for a given aspect ratio."""
        return 64 * aspect_ratio


    @ParSpace(logra=range(4, 7),
              aspect_ratio=[2, 4, 8])
    def submit_jobs(**pars):
        """Create run directory, parameter file, and submit a job."""
        case_name = 'ra_1e{logra}__asp_{aspect_ratio}'.format(**pars)
        case_dir = ROOT / case_name

        # create run directory, in this case a subdirectory "output"
        # is also created.
        (case_dir / 'output').mkdir(parents=True, exist_ok=True)

        # generate par file, this assumes a JSON parameter file
        asp = pars['aspect_ratio']
        par_content = dict(rayleigh=10**pars['logra'],
                           aspect_ratio=pars['aspect_ratio'],
                           ny=n_horiz(asp))
        par_file = case_dir / 'par.json'
        with par_file.open('w') as pstream:
            json.dump(par_content, pstream)

        batch_content = BATCH.format(work_dir=case_dir)
        batch_file = case_dir / 'batch'
        batch_file.write_text(batch_content)

        job_sub = subprocess.run((QSUB, str(batch_file)),
                                 capture_output=True, check=True, text=True)
        job_id = job_sub.stdout.splitlines()[-1].split('.')[0]
        print(f"Case {case_name} treated by {job_id}")


    if __name__ == "__main__":
        submit_jobs()
