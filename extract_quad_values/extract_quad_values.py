import mmltools
import sys, json

with open('b2_template.json') as file:
    template_lattice = json.load(file)

if len(sys.argv) > 1:
    paths = sys.argv[1:]
else:
    print('DEBUG')
    paths = ['ATRingWithAO.mat']

for path in paths:
    print(path)
    lwa = mmltools.ATRingWithAO(path)
    quads = lwa.get_magnet_strength(at_type='QUAD', method='byPowerSupply')
    # sexts = lwa.get_magnet_strength(at_type='SEXT', method='byPowerSupply')

    new_lattice = template_lattice.copy()
    new_lattice['elements'] = {**quads, **template_lattice['elements']}
    print(f'extracted quad_values for {path}')
    print(json.dumps(new_lattice, indent=2))
    with open(f'{path}_lattice.json', 'w') as file:
        json.dump(new_lattice, file, indent=2)
