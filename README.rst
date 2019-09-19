Demos
=====
A collection of demos using the D-Wave Ocean SDK.

**NOTE** Each demo is stored in its own subdirectory and may have its own
set of package requirements (for example, `antenna-selection/requirements.txt
<antenna-selection/requirements.txt>`_).

Setup Instructions
------------------
As each demo may have a different set of package requirements, you may want to
set up a `virtual environment <https://docs.ocean.dwavesys.com/en/latest/overview/install.html#python-virtual-environment>`_
to contain said packages and run your demo within that environment.

Package Installation
~~~~~~~~~~~~~~~~~~~~
::

  git clone git@github.com:dwavesystems/demos.git
  cd demos/<desired-demo>
  pip install -r requirements.txt

Please note that as the demos will be using the Ocean SDK, they will likely
need access to a D-Wave system. If you are accessing this for the first time,
you will need to:
* Sign up for `D-Wave Leap <https://cloud.dwavesys.com/leap/signup/>`_ in order
  to get an Authentication token
* Create a `configuration file <https://docs.ocean.dwavesys.com/en/latest/overview/dwavesys.html#configuring-a-d-wave-system-as-a-solver>`_

Now you're ready to run your demo!

