
from seisflows.tools.config import loadclass

class Thomsen_hti(loadclass('solver', 'Thomsen_base')):

    # model parameters included in inversion
    parameters = []
    parameters += ['vp']
    parameters += ['vs']
    parameters += ['epsilon']
    parameters += ['delta']
    parameters += ['gamma']
    parameters += ['azimuth']

