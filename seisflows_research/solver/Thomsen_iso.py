from seisflows.tools.config import loadclass, ParameterObj

PAR = ParameterObj('SeisflowsParameters')
PATH = ParameterObj('SeisflowsPaths')


class Thomsen_iso(loadclass('solver', 'Thomsen_base')):

    # model parameters included in inversion
    inversion_parameters = []
    inversion_parameters += ['vp']
    inversion_parameters += ['vs']

