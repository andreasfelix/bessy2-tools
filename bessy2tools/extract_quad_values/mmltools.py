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
        self.at_indices = np.zeros(N, dtype=int)
        self.ao_indices = np.zeros(N, dtype=int)
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
        print(f'{"index":5} {"at_indices":5} {"ao_indices":5}  {"at_names":12}    {"ao_names":12}   '
              f'{"ps_names":20}   {"at_types (defined in AO)":20}')
        for i in range(n_max if n_max is not None else self.N):
            print(f'{i:6n}  {self.at_indices[i]:6n}  {self.ao_indices[i]:6n}  {self.at_names[i]:12}    '
                  f'{self.ao_names[i]:12}   {self.ps_names[i]:20}   {self.at_types[i]:20}')


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
                print(f'start: {s - l:12.6f} - {s:10.6f}   length: {l:10.5f}   ', f'{i:5n} {name:12}  {type_name:20}',
                      extra)

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

        print(f'Locofile belongs to: {self.ad.Maschine}')

        # loop over AO entries to fill name_map
        for family_name in self.ao._fieldnames:
            # getattr will return the value for the given key
            if family_name in ('TUNE', 'DCCT'):
                continue
            family_object = getattr(self.ao, family_name)[0, 0]
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

    def _get_magnet_strength(self, name, strength, at_type):
        if self.ad.Maschine == 'BESSYII':
            quad_length = {'Q1': 0.25, 'Q2': 0.20, 'Q3': 0.25, 'Q4': 0.50, 'Q5': 0.20, 'QI': 0.122}
            sext_length = {'S1': 0.21, 'S2': 0.16, 'S3': 0.16, 'S4': 0.16}
            name = name.replace('PR', '').replace('PD', 'D').replace('PT', 'T').replace('PQ', 'Q').replace('R', '')
        elif self.ad.Maschine == 'MLS':
            quad_length = {'Q1': 0.2, 'Q2': 0.2, 'Q3': 0.2}
            sext_length = {'S1': 0.1, 'S2': 0.1, 'S3': 0.1}
            name = name.replace('RP', '')
        else:
            raise Exception('Unkown Maschine.')

        if at_type == 'QUAD':
            return {name: dict(type="Quad", length=quad_length[name[:2]], k1=strength)}
        elif at_type == 'SEXT':
            if name == 'S1':
                print('! Note: Is S1 split? -> change length to 0.105')
            length = sext_length[name[:2]]
            return {name: dict(type="Sext", length=sext_length, k2=strength / length * 2)}
        else:
            print("Unkown at type!")

    def get_magnet_strength(self, at_type='QUAD', fit_iteration=-1, method='byPowerSupply'):
        r = self.rings[fit_iteration].ring[0, :]

        get_strength = {'QUAD': lambda i: r[i][0, 0].K[0, 0], 'SEXT': lambda i: r[i][0, 0].PolynomB[0, 2]}[at_type]

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
                        print('WARNING: Differnt elements of same power supply have differnt values!'
                              'Probably not fitted according to Power supply! Using average value!')
                    average_strength += get_strength(i)
                average_strength = average_strength / len(at_indices)
                elements.update(self._get_magnet_strength(ps_name, average_strength, at_type))
            return elements
        else:
            raise Exception('Method not implemented.')
