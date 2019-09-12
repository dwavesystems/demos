Demos
=====
A collection of demos using the D-Wave Ocean SDK.

**NOTE** Each demo is stored in its own subdirectory and may have its own
set of package requirements (see <desired-demo>/requirements.txt).

Setup Instructions
------------------
As each demo may have a different set of package requirements, you may want to
set up a virtual environment to contain said packages and run your demo within
that environment.

Setting up a virtual environment and installing package requirements:
::

  git clone git@github.com:dwavesystems/demos.git
  cd demos/<desired-demo>
  python -m venv <desired-demo>_env
  source <desired-demo>_env/bin/activate
  pip install -r requirements.txt

Once your virtual environment has been *activated* (see
``source <desired-demo>_env/bin/activate``) and the package requirements have
been installed, you can run your demo.

When you're ready to deactivate your virtual environment, simply type:
::
  deactivate

When you want to run your demo again, remember to activate your virtual
environment before running.

