
from glob import glob

import numpy as np

from seisflows.tools import unix
from seisflows.tools.code import exists
from seisflows.tools.config import SeisflowsParameters, SeisflowsPaths, \
    ParameterError

from seisflows.seistools import adjoint

PAR = SeisflowsParameters()
PATH = SeisflowsPaths()

import system
import solver
import preprocess
import postprocess


class compute_precond(object):

    def check(self):
        """ Checks parameters and paths
        """
        # check paths
        if 'GLOBAL' not in PATH:
            raise ParameterError(PATH, 'GLOBAL')

        if 'LOCAL' not in PATH:
            setattr(PATH, 'LOCAL', None)

        if 'OUTPUT' not in PATH:
            raise ParameterError(PATH, 'OUTPUT')

        # check input
        if 'DATA' not in PATH:
            setattr(PATH, 'DATA', None)

        if 'MODEL_INIT' not in PATH:
            raise ParameterError(PATH, 'MODEL_INIT')

        if 'CLIP' not in PAR:
            setattr(PAR, 'CLIP', 0.)

        # assertions
        0. <= PAR.CLIP <= 1.


    def main(self):
        path = PATH.GLOBAL

        # prepare directory structure
        unix.rm(path)
        unix.mkdir(path)

        # set up workflow machinery
        preprocess.setup()
        postprocess.setup()

        system.run('solver', 'setup',
                   hosts='all')

        print 'Generating preconditioner...'
        system.run('solver', 'generate_precond',
                   hosts='all',
                   process_traces=process_traces,
                   model_path=PATH.MODEL_INIT,
                   model_name='model',
                   model_type='gll')

        postprocess.combine_kernels(
            path=path,
            parameters=solver.parameters)

        for span in getlist(PAR.SMOOTH):
            self.process_kernels(
                path=path,
                parameters=solver.parameters,
                span=span)

            # save preconditioner
            src = path +'/'+ 'kernels/absval'
            dst = PATH.OUTPUT +'/'+ 'precond_%04d' % span
            unix.cp(src, dst)

        print 'Finished\n'


    def process_kernels(self, path, parameters, span):
        assert exists(path)
        assert len(parameters) > 0

        # take absolute value
        parts = solver.load(path +'/'+ 'kernels/sum', suffix='_kernel')
        for key in parameters:
            parts[key] = np.abs(parts[key])

        self._save(path, parts)


        # smooth
        system.run('solver', 'smooth',
                   hosts='head',
                   path=path +'/'+ 'kernels/absval',
                   parameters=parameters,
                   span=span)

        # normalize
        parts = solver.load(path +'/'+ 'kernels/absval', suffix='_kernel')
        for key in parameters:
            parts[key] = np.mean(parts[key])/parts[key]

        self._save(path, parts)



    def _save(self, path, parts):
        solver.save(path +'/'+ 'kernels/absval',
                    parts,
                    suffix='_kernel')


    def _load(path, parameters, prefix='', suffix=''):
        parts = {}
        for key in parameters:
            parts[key] = []

        for iproc in range(solver.mesh.nproc):
            # read database files
            keys, vals = loadbypar(path, parameters, iproc, prefix, suffix)
            for key, val in zip(keys, vals):
                parts[key] += [val]
        return parts



def process_traces(path):
    unix.cd(path)

    d, h = preprocess.load(prefix='traces/obs/')
    s, h = preprocess.load(prefix='traces/syn/')

    s = preprocess.apply(adjoint.precond2, [s, d], [h])

    preprocess.save(s, h, prefix='traces/adj/')


def getlist(var):
    if isinstance(var, list):
        return var

    if isinstance(var, float):
        return [var]

    if isinstance(var, int):
        return [var]


