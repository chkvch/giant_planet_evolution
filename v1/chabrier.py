from scipy.interpolate import RectBivariateSpline as rbs
from itertools import islice
import numpy as np

class eos:
    def __init__(self, path_to_data=None):

        if not path_to_data:
            import os
            path_to_data = os.environ['ongp_data_path']

        npts_t = 121
        npts_t -= 60 # skip logT < 5; there are 60 such points
        npts_p = 441
        # - The (log T, log P) tables include NT=121 isotherms
        # between logT=2.0 and logT=8.0 with a step dlogT=0.05.
        # Each isotherm includes NP=441 pressures from
        # logP=-9.0 to log P=+13.0 with a step dlogP=0.05.

#log T [K]        log P [GPa]   log rho [g/cc]  log U [MJ/kg] log S [MJ/kg/K]  dlrho/dlT_P,  dlrho/dlP_T,   dlS/dlT_P,     dlS/dlP_T         grad_ad
        columns = 'logt', 'logp', 'logrho', 'logu', 'logs', 'rhot', 'rhop', 'st', 'sp'
        h_path = f'{path_to_data}/DirEOS2019/TABLE_H_TP_v1'
        he_path = f'{path_to_data}/DirEOS2019/TABLE_HE_TP_v1'
        self.logtvals = np.array([])

        self.data = {}
        for component in ('h', 'he'):
            path = {'h':h_path, 'he':he_path}[component]
            self.data[component] = {}
            for name in columns:
                self.data[component][name] = np.zeros((npts_p, npts_t))
            it = 0
            with open(path, 'r') as f:
                for i, line in enumerate(f.readlines()):
                    if line[0] == '#':
                        if '=' in line:
                            if float(line.split()[-1]) > 5:
                                continue
                            with open(path, 'rb') as g:
                                chunk = np.genfromtxt(islice(g, i+1, i+npts_p+1), names=columns)
                            for name in columns:
                                self.data[component][name][:, it] = chunk[name]
                            if component == 'h':
                                # count new t points just once
                                self.logtvals = np.append(self.logtvals, chunk['logt'][0])
                            it += 1
            self.data[component]['logp'] += 10 # 1 GPa = 1e10 cgs
            self.data[component]['logu'] += 10 # 1 MJ/kg = 1e13 erg/kg = 1e10 erg/g
            self.data[component]['logs'] += 10 # 1 MJ/kg = 1e13 erg/kg = 1e10 erg/g

        self.logpvals = chunk['logp'] + 10 # logps are always the same, just grab from last chunk read
        self.spline_kwargs = {'kx':3, 'ky':3}

    def get_logrho_h(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['h']['logrho'], **self.spline_kwargs)(lgp, lgt, grid=False)
    def get_logs_h(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['h']['logs'], **self.spline_kwargs)(lgp, lgt, grid=False)
    def get_rhop_h(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['h']['rhop'], **self.spline_kwargs)(lgp, lgt, grid=False)
    def get_rhot_h(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['h']['rhot'], **self.spline_kwargs)(lgp, lgt, grid=False)
    def get_sp_h(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['h']['sp'], **self.spline_kwargs)(lgp, lgt, grid=False)
    def get_st_h(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['h']['st'], **self.spline_kwargs)(lgp, lgt, grid=False)

    def get_logrho_he(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['he']['logrho'], **self.spline_kwargs)(lgp, lgt, grid=False)
    def get_logs_he(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['he']['logs'], **self.spline_kwargs)(lgp, lgt, grid=False)
    def get_rhop_he(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['he']['rhop'], **self.spline_kwargs)(lgp, lgt, grid=False)
    def get_rhot_he(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['he']['rhot'], **self.spline_kwargs)(lgp, lgt, grid=False)
    def get_sp_he(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['he']['sp'], **self.spline_kwargs)(lgp, lgt, grid=False)
    def get_st_he(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['he']['st'], **self.spline_kwargs)(lgp, lgt, grid=False)

    # testing shows that getting derivative on spline actually does a better job of yielding a grada
    # that, when integrated, gives a profile corresponding to constant entropy in this eos
    def get_sp_h_alt(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['h']['logs'], **self.spline_kwargs)(lgp, lgt, grid=False, dx=1)
    def get_st_h_alt(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['h']['logs'], **self.spline_kwargs)(lgp, lgt, grid=False, dy=1)
    def get_sp_he_alt(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['he']['logs'], **self.spline_kwargs)(lgp, lgt, grid=False, dx=1)
    def get_st_he_alt(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['he']['logs'], **self.spline_kwargs)(lgp, lgt, grid=False, dy=1)
    # see if doing same for partials of rho helps give a more reliable gamma1
    def get_rhop_h_alt(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['h']['logrho'], **self.spline_kwargs)(lgp, lgt, grid=False, dx=1)
    def get_rhot_h_alt(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['h']['logrho'], **self.spline_kwargs)(lgp, lgt, grid=False, dy=1)
    def get_rhop_he_alt(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['he']['logrho'], **self.spline_kwargs)(lgp, lgt, grid=False, dx=1)
    def get_rhot_he_alt(self, lgp, lgt):
        return rbs(self.logpvals, self.logtvals, self.data['he']['logrho'], **self.spline_kwargs)(lgp, lgt, grid=False, dy=1)


    # general method for getting quantities for hydrogen-helium mixture
    def get(self, logp, logt, y):
        s_h = 10 ** self.get_logs_h(logp, logt)
        s_he = 10 ** self.get_logs_he(logp, logt)
        # sp_h = self.get_sp_h(logp, logt)
        # st_h = self.get_st_h(logp, logt)
        # sp_he = self.get_sp_he(logp, logt)
        # st_he = self.get_st_he(logp, logt)
        sp_h = self.get_sp_h_alt(logp, logt)
        st_h = self.get_st_h_alt(logp, logt)
        sp_he = self.get_sp_he_alt(logp, logt)
        st_he = self.get_st_he_alt(logp, logt)


        s = (1. - y) * s_h + y * s_he # + smix # can add smix via eq. (11) of CMS19; about 0.23 kb/mp for Y=0.275
        st = (1. - y) * s_h / s * st_h + y * s_he / s * st_he # + smix/s*dlogsmix/dlogt # CMS19 include no T or P dependence in smix
        sp = (1. - y) * s_h / s * sp_h + y * s_he / s * sp_he # + smix/s*dlogsmix/dlogp # CMS19 include no T or P dependence in smix
        grada = - sp / st

        rho_h = 10 ** self.get_logrho_h(logp, logt)
        rho_he = 10 ** self.get_logrho_he(logp, logt)
        rhoinv = y / rho_he + (1. - y) / rho_h
        rho = rhoinv ** -1.
        logrho = np.log10(rho)
        # rhop_h = self.get_rhop_h(logp, logt)
        # rhot_h = self.get_rhot_h(logp, logt)
        # rhop_he = self.get_rhop_he(logp, logt)
        # rhot_he = self.get_rhot_he(logp, logt)
        rhop_h = self.get_rhop_h_alt(logp, logt)
        rhot_h = self.get_rhot_h_alt(logp, logt)
        rhop_he = self.get_rhop_he_alt(logp, logt)
        rhot_he = self.get_rhot_he_alt(logp, logt)

        rhot = (1. - y) * rho / rho_h * rhot_h + y * rho / rho_he * rhot_he
        rhop = (1. - y) * rho / rho_h * rhop_h + y * rho / rho_he * rhop_he

        chirho = 1. / rhop # dlnP/dlnrho|T
        chit = -1. * rhot / rhop # dlnP/dlnT|rho
        # gamma1 = 1. / (sp ** 2 / st + rhop) # dlnP/dlnrho|s
        chiy = -1. * rho * y * (1. / rho_he - 1. / rho_h) # dlnrho/dlnY|P,T

        gamma1 = chirho / (1. - chit * grada)
        gamma3 = 1. + gamma1 * grada
        cp = s * st
        cv = cp * chirho / gamma1 # Unno 13.87
        csound = np.sqrt(10 ** logp / rho * gamma1)

        # grada_ = - ((1. - y) * s_h * sp_h + y * s_he * sp_he) / ((1. - y) * s_h * st_h + y * s_he * st_he)
        #
        # sp_h_alt = self.get_sp_h_alt(logp, logt)
        # st_h_alt = self.get_st_h_alt(logp, logt)
        # sp_he_alt = self.get_sp_he_alt(logp, logt)
        # st_he_alt = self.get_st_he_alt(logp, logt)
        # grada_alt = - ((1. - y) * s_h * sp_h_alt + y * s_he * sp_he_alt) / ((1. - y) * s_h * st_h_alt + y * s_he * st_he_alt)

        res =  {
            'grada':grada,
            'logrho':logrho,
            'logs':np.log10(s),
            'logs_h':np.log10(s_h),
            'logs_he':np.log10(s_he),
            'gamma1':gamma1,
            'chirho':chirho,
            'chit':chit,
            'gamma1':gamma1,
            'gamma3':gamma3,
            'chiy':chiy,
            'rho_h':rho_h,
            'rho_he':rho_he,
            'rhop':rhop,
            'rhot':rhot,
            'cp':cp,
            'cv':cv,
            'csound':csound
            }
        return res

    def get_grada(self, logp, logt, y):
        return self.get(logp, logt, y)['grada']

    def get_logrho(self, logp, logt, y):
        return self.get(logp, logt, y)['logrho']

    def get_logs(self, logp, logt, y):
        # return self.get(logp, logt, y)['logs']
        s_h = 10 ** self.get_logs_h(logp, logt)
        s_he = 10 ** self.get_logs_he(logp, logt)
        sp_h = self.get_sp_h(logp, logt)
        st_h = self.get_st_h(logp, logt)
        sp_he = self.get_sp_he(logp, logt)
        st_he = self.get_st_he(logp, logt)

        s = (1. - y) * s_h + y * s_he # + smix
        return np.log10(s)

    def get_gamma1(self, logp, logt, y):
        return self.get(logp, logt, y)['gamma1']
