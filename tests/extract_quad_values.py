from bessy2tools.extract_quad_values import mmltools
from python_utils.profile import profile


# Example application to extract Quadrupole and Sextupole values in elegant
# notation from a .mat file created in ATRingWithAO format.

# @profile
def test():
    lwa = mmltools.ATRingWithAO('ATRingWithAO.mat')
    quads = lwa.get_magnet_strength(at_type='QUAD', method='byPowerSupply')
    sexts = lwa.get_magnet_strength(at_type='SEXT', method='byPowerSupply')
    return quads, sexts


test()
