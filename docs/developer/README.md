
# README

Requirements
============

You must build the documentation on a valid gtk-x11 platform.  This
means that platform-specific documentation is for gtk-x11.

You must be able to build m7 on gtk-x11.  This means you'll need to
have all the requirements to run ``run.sh`` in ``tv/platform/gtk-x11/``.

You must have the Sphinx documentation tools installed.  On Ubuntu,
this is usually as easy as::

    sudo apt-get install python-sphinx


Building the docs
=================

To build the docs, run::

    make html

If documentation building is successful, then it will be in the
``./_build/html/`` directory.

To clean everything::

    make clean
