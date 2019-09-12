Demos
=====
A collection of demos using the D-Wave Ocean SDK.

**NOTE** Each demo is stored in its own subdirectory and may have its own
set of package requirements (for example, `antenna-selection/requirements.txt
<antenna-selection/requirements.txt>`_).

Setup Instructions
------------------
As each demo may have a different set of package requirements, you may want to
set up a virtual environment to contain said packages and run your demo within
that environment.

Virtual environment setup and package installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

  git clone git@github.com:dwavesystems/demos.git
  cd demos/<desired-demo>
  python3 -m venv <desired-demo>_env
  source <desired-demo>_env/bin/activate
  pip install -r requirements.txt

Once the commands above have created and activated your virtual environment,
and installed the package requirements, you can run your demo.

Virtual environment deactivation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Once you're ready to leave your virtual environment, simply type:
::
  deactivate

When you want to run your demo again, remember to activate your virtual
environment first:
::
  source <desired-demo>_env/bin/activate

Note to Python 2.7 users
~~~~~~~~~~~~~~~~~~~~~~~~
Python 2.7 does not ship with ``venv``, so in that case, instead of the command
``python3 -m venv <desired-demo>_env``, do the following:
::
  pip install virtualenv
  virtualenv <desired-demo>_env

