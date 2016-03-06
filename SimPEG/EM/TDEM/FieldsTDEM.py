import numpy as np
import scipy.sparse as sp
import SimPEG
from SimPEG import Utils
from SimPEG.EM.Utils import omega
from SimPEG.Utils import Zero, Identity

class Fields(SimPEG.Problem.TimeFields):
    """
    
    Fancy Field Storage for a TDEM survey. Only one field type is stored for
    each problem, the rest are computed. The fields obejct acts like an array and is indexed by

    .. code-block:: python

        f = problem.fields(m)
        e = f[srcList,'e']
        b = f[srcList,'b']

    If accessing all sources for a given field, use the :code:`:`

    .. code-block:: python

        f = problem.fields(m)
        e = f[:,'e']
        b = f[:,'b']

    The array returned will be size (nE or nF, nSrcs :math:`\\times` nFrequencies)
    """

    knownFields = {}
    dtype = float 

class Fields_Derivs(Fields):
    knownFields = {
                    'bDeriv': 'F',
                    'eDeriv': 'E',
                    'hDeriv': 'E',
                    'jDeriv': 'F'
                  }
                  

class Fields_b(Fields):
    """Fancy Field Storage for a TDEM survey."""
    knownFields = {'bSolution': 'F'}
    aliasFields = {
                    'b': ['bSolution', 'F', '_b'],
                    'e': ['bSolution', 'E', '_e'],
                  }

    def startup(self):
        self.MeSigmaI = self.survey.prob.MeSigmaI
        self.edgeCurl = self.survey.prob.mesh.edgeCurl
        self.MfMui    = self.survey.prob.MfMui

    def _b(self, bSolution, srcList, tInd):
        return bSolution

    def _bDeriv_u(self, src, dun_dm_v, adjoint = False):
        return Identity()*dun_dm_v

    def _bDeriv_m(self, src, v, adjoint = False):
        return Zero()

    def _bDeriv(self, src, dun_dm_v, v, adjoint=False): 
        if adjoint is True:
            raise NotImplementedError
        return self._bDeriv_u(src, dun_dm_v) + self._bDeriv_m(src, v)

    def _e(self, bSolution, srcList, tInd):
        e = self.MeSigmaI * ( self.edgeCurl.T * ( self.MfMui * bSolution ) )
        for i, src in enumerate(srcList):
            _, S_e = src.eval(self.prob, tInd) 
            e[:,i,tInd] = e[:,i,tInd] - self.MeSigmaI * S_e
        return e  

    def _eDeriv_u(self, src, dun_dm_v, adjoint = False):
        raise NotImplementedError

    def _eDeriv_m(self, src, v, adjoint = False):
        raise NotImplementedError

