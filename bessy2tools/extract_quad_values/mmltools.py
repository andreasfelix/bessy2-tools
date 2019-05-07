import numpy as np
import scipy.io as sio

class NameMap:
    """
    A global table with
    AT index (python convention) - AT ('family')name - AO name - PS name - at_types (defined in AO!)
    NOTE: starts at ZERO (python style), not ONE (MatLab style)
    NOTE: ao_indices is not unique but is defined in each family (for each at_names)
    """

    def __init__(self, N):
        self.N = N
        self.at_indices = np.zeros(N)
        self.ao_indices = np.zeros(N)
        self.at_types = np.array([''] * N, dtype="U40")
        self.at_names = np.array([''] * N, dtype="U40")
        self.ao_names = np.array([''] * N, dtype="U40")
        self.ps_names = np.array([''] * N, dtype="U40")

    def get_at_indices_by_ao_names(self, name):
        return self.at_indices[self.ao_names == name]

    def get_at_indices_by_ps_names(self, name):
        return self.at_indices[self.ps_names == name]

    def get_at_indices_by_at_names(self, name):
        return self.at_indices[self.at_names == name]

    def get_ps_names(self, at_type='QUAD'):
        return np.unique(self.ps_names[self.at_types == at_type])

    def get_ao_names(self, at_type='QUAD'):
        return np.unique(self.ao_names[self.at_types == at_type])

    def get_at_names(self, at_type='QUAD'):
        return np.unique(self.at_names[self.at_types == at_type])

    def print_name_map(self, n_max=None):
        print(f' {"index":5} {"at_indices":5} {"ao_indices":5}  {"at_names":12}    {"ao_names":12}   {"ps_names":20}   {"at_types (defined in AO)":20}')
        for i in range(n_max if n_max is not None else self.N):
            print(f'{i:6n}  {self.at_indices[i]:6n}  {self.ao_indices[i]:6n}  {self.at_names[i]:12}    {self.ao_names[i]:12}   {self.ps_names[i]:20}   {self.at_types[i]:20}')


class PrintATRing:
    """ can deal with a MatLab AT RING objection """

    def __init__(self, r, details='default'):
        nat_elements = len(r)
        s = 0
        for i in range(nat_elements):
            name = r[i][0, 0].FamName[0]
            type_name = r[i][0, 0].PassMethod[0]
            l = r[i][0, 0].Length[0, 0]
            s = s + l
            if i >= 0:  # s <= 320 and
                extra = ''
                if type_name in ('StrMPoleSymplectic4Pass', 'StrMPoleSymplectic4RadPass'):
                    try:
                        K = r[i][0, 0].K[0, 0]
                        extra += f' K = {K:11.8f}'
                    except:
                        K = r[i][0, 0].PolynomB[0, 2]
                        extra += f' PolynomB[0,2] = {K:11.8f}'
                if type_name in ('ThinMPolePass'):
                    K = r[i][0, 0].PolynomB[0, 2]
                    extra += f' PolynomB[0,2] = {K:11.8f}'
                if type_name in ('BndMPoleSymplectic4Pass', 'BndMPoleSymplectic4RadPass'):
                    BendingAngle = r[i][0, 0].BendingAngle[0, 0]
                    EntranceAngle = r[i][0, 0].EntranceAngle[0, 0]
                    ExitAngle = r[i][0, 0].ExitAngle[0, 0]
                    extra += f' BendingAngle = {BendingAngle:11.8f} EntranceAngle = {EntranceAngle:11.8f} ExitAngle = {ExitAngle:11.8f}'

                if extra == '' and details == 'default':
                    continue
                print(f'start: {s - l:12.6f} - {s:10.6f}   length: {l:10.5f}   ', f'{i:5n} {name:12}  {type_name:20}', extra)

        print(f'Total length: {s:12.6f}')

class ATRingWithAO:
    def __init__(self, filename):
        # struct_as_record=False preserves nested dictionaries!
        self.mat_dict = sio.loadmat(filename, struct_as_record=False, squeeze_me=False)

        self.ao = self.mat_dict['ao'][0][0]
        self.ad = self.mat_dict['ad'][0][0]
        self.ad = self.mat_dict['ad'][0][0]
        self.rings = self.mat_dict['RINGs'][0, :]
        r = self.rings[0].ring[0, :]

        self.n_at_elements = len(r)
        self.name_map = NameMap(self.n_at_elements)

        # loop over AO entries to fill name_map
        for family_name in self.ao._fieldnames:
            # getattr will return the value for the given key
            if family_name in ('TUNE', 'DCCT'):
                continue
            family_object = getattr(self.ao, family_name)[0, 0]
            # continue
            at_indices = family_object.AT[0, 0].ATIndex
            at_type = family_object.AT[0, 0].ATType[0]
            ao_names = family_object.CommonNames
            ps_names = family_object.Monitor[0, 0].ChannelNames
            if family_name == 'RF':
                ao_names = np.repeat(ao_names, len(at_indices))
                ps_names = np.repeat(ps_names, len(at_indices))
            n_1st, n_2nd = at_indices.shape
            for i_2nd in range(n_2nd):
                for i_1st in range(n_1st):
                    j = at_indices[i_1st, i_2nd] - 1
                    self.name_map.at_indices[j] = j  # note: start at zero (python style)
                    self.name_map.ao_indices[j] = i_1st  # note: start at zero (python style)
                    self.name_map.at_types[j] = at_type
                    self.name_map.ao_names[j] = ao_names[i_1st]
                    self.name_map.ps_names[j] = ps_names[i_1st].split(':')[0]

        # loop over RING to fill additionally with AT ('family') name
        for i, x in enumerate(r):
            self.name_map.at_names[i] = x[0, 0].FamName[0]

        # some consistency checks
        for at_name, ps_name in zip(self.name_map.at_names, self.name_map.ps_names):
            if at_name == 'BEND' and ps_name not in ('PB1ID6R', 'PB2ID6R', 'PB3ID6R', 'BPR', 'BPRP'):
                raise Exception('ERROR : BROKEN FILE!!! Probable cause: init and AT file incompatible!!!')

    def get_ring(self, fit_iteration=-1):
        return self.rings[fit_iteration].ring[0, :]

    def _get_magnet_strength(self, name, strength, at_type):
        if self.ad.Machine == 'BESSYII':
            quad_length = {'Q1': 0.25, 'Q2': 0.20, 'Q3': 0.25, 'Q4': 0.50, 'Q5': 0.20, 'PQIT6R': 0.122}
            sext_length = {'S1': 0.21, 'S2': 0.16, 'S3': 0.16, 'S4': 0.16}
            name = name.replace('PR', '').replace('PD', 'D').replace('PT', 'T').replace('PQ', 'Q').replace('R', '')
        elif self.ad.Machine == 'MLS':
            quad_length = {'Q1': 0.2, 'Q2': 0.2, 'Q3': 0.2}
            sext_length = {'S1': 0.1, 'S2': 0.1, 'S3': 0.1}
            name = name.replace('RP', '')
        else:
            raise Exception('Unkown Machine.')

        if at_type == 'SEXT':
            length = sext_length[name[:2]]
            strength = strength / length * 2
            if name == 'S1':
                print('! Note: Is S1 split? -> change length to 0.105')

        if at_type == 'QUAD':
            length = quad_length[name[:2]]

        return {name: dict(type=at_type, length=length, strength=strength)}

    def get_magnet_strength(self, at_type='QUAD', fit_iteration=-1, method='byPowerSupply'):
        print(f'Locofile belongs to: {self.ad.Machine}')
        r = self.rings[fit_iteration].ring[0, :]

        if at_type == 'QUAD':
            get_strength = lambda i: r[i][0, 0].K[0, 0]
        elif at_type == 'SEXT':
            get_strength = lambda i: r[i][0, 0].PolynomB[0, 2]
        else:
            raise Exception('at_type not implemented.')

        if method == 'byPowerSupply':
            print(f'List magnet ({at_type}) strength by power supply.')
            ps_names = self.name_map.get_ps_names(at_type=at_type)
            print(f'Number of independent parameters: {len(ps_names)}')
            elements = {}
            for ps_name in ps_names:
                at_indices = self.name_map.get_at_indices_by_ps_names(ps_name)
                strength = get_strength(at_indices[0])
                average_strength = 0
                for i in at_indices:
                    if strength != get_strength(i):  # r[i][0,0].K[0,0]:
                        print('WARNING: Differnt elements of same power supply have differnt values! Probably not fitted according to Power supply! Using average value!')
                    average_strength += get_strength(i)
                average_strength = average_strength / len(at_indices)
                elements.update(**self._get_magnet_strength(ps_name, average_strength, at_type))
            return elements
        else:
            raise Exception('Method not implemented.')

    def getArchiverScalar(self, var, t):
        # from AS archiver.py module and modified
        from urllib2 import urlopen, quote
        import datetime

        def filter_camonitor(data):
            while True:
                a, = next(data),
                if not a.startswith('#'):
                    s = a.split()
                    if len(s) == 3:
                        s += ['0']
                    yield ' '.join([s[0], s[1] + '+' + s[2], s[3]])
                else:
                    yield a

        def archiver(var, t0, t1, archive='master'):
            if archive == 'current_week':
                bii = "http://archiver.bessy.de/archive/cgi/CGIExport.cgi?INDEX=/opt/Archive/current_week/index&COMMAND=camonitor"
            else:
                if archive != 'master':
                    print('WARNING unknown archive', archive)
                bii = "http://archiver.bessy.de/archive/cgi/CGIExport.cgi?INDEX=/opt/Archive/master_index&COMMAND=camonitor"

            if self.ad.Machine == 'MLS':
                bii = "http://arc31c.trs.bessy.de/MLS/cgi/CGIExport.cgi?INDEX=%2Fopt%2FArchive%2Fmaster_index&COMMAND=camonitor"

            if type(var) is list:
                var = '\n'.join(var)

            var = "&NAMES=%s" % quote(var)
            spec = "&STRSTART=1&STARTSTR=%s&STREND=1&ENDSTR=%s" % (quote(t0), quote(t1))
            res = urlopen(bii + spec + var)

            return np.genfromtxt(filter_camonitor(res), dtype=None, names=('name', 'time', 'value'), converters={1: lambda d: datetime.datetime.strptime(d[:-3], '%Y-%m-%mat_dict+%H:%M:%S.%f')})

        def archiverScalar(var, t):
            return float(archiver(var, t, t)['value'])

        return archiverScalar(var, t)

    def getMagnetStrengthOnline(self, source='archiver', time='2016-07-28 11:00:00', ATtype='QUAD', method='byPowerSupply', outputstyle='visual'):
        if self.ad.Machine == 'MLS':
            suffix = ':setCur'
            suffixstat1 = ':stPower'
        else:
            suffix = ':set'
            suffixstat1 = ':stat1'
        if source == 'epics':
            from epics import PV
            import datetime
            time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%mat_dict %H:%M:%S')

        if method == 'byPowerSupply':
            print('List magnet ({0}) strength by power supply. Source: {1} (time: {2}).'.format(ATtype, source, time))

            ps_names = self.name_map.get_ps_names(at_type=ATtype)
            print('Number of independent parameters:', len(ps_names))
            for name in ps_names:
                # take first element
                field = self.name_map.at_names[self.name_map.get_at_indices_by_ps_names(name)][0]
                conversionfactors = getattr(self.ao, field)[0, 0].Monitor[0, 0].HW2PhysicsParams[:, 0]
                if self.ad.Machine == 'MLS':
                    # TODO: not understood why needed!?
                    conversionfactors = conversionfactors[0][:, 0]
                cfac = np.mean(conversionfactors)
                if not np.array_equal(conversionfactors, conversionfactors[0] * np.ones_like(conversionfactors)):
                    raise Exception('Warning: Different conversion factors for a single power supply given! Taking average.')

                if source == 'archiver':
                    Savg = cfac * self.getArchiverScalar(name + suffix, time)
                    stat1 = self.getArchiverScalar(name + suffixstat1, time)
                    Savg *= stat1
                elif source == 'epics':
                    Savg = cfac * PV(name + suffix).get()
                else:
                    raise Exception('Source not implemented.')

                self._get_magnet_strength(name, Savg, ATtype, outputstyle)
        else:
            print('Method not implemented.')
