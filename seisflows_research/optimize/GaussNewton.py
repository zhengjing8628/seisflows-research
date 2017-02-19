import numpy as np

from seisflows.tools import unix
from seisflows.tools.array import loadnpy, savenpy
from seisflows.tools.tools import loadtxt, savetxt
from seisflows.config import , \
    ParameterError, custom_import

from seisflows.optimize import lib

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class GaussNewton(custom_import('optimize', 'Newton')):
    """ Adds Gauss-Newton-CG algorithm to nonlinear optimization base class
    """

    def check(cls):
        """ Checks parameters and paths
        """
        if 'SCHEME' not in  PAR:
            setattr(PAR, 'SCHEME', 'GaussNewton')

        super(GaussNewton, cls).check()


    def hessian_product(cls, g, h):
        unix.cd(PATH.OPTIMIZE)

        dg = loadnpy('g_lcg')

        print 'minmax dg:', min(dg), max(dg)

        return h**-1 * dg

