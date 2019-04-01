quadlist_epics = ['PQIT6R', 'Q1PDR', 'Q2PDR', 'Q3P1T1R', 'Q3P1T6R', 'Q3P1T8R', 'Q3P2T1R', 'Q3P2T6R',
                    'Q3P2T8R', 'Q3PD1R', 'Q3PD2R', 'Q3PD3R', 'Q3PD4R', 'Q3PD5R', 'Q3PD6R', 'Q3PD7R',
                    'Q3PD8R', 'Q3PT2R', 'Q3PT3R', 'Q3PT4R', 'Q3PT5R', 'Q3PT7R', 'Q4P1T1R', 'Q4P1T6R',
                    'Q4P1T8R', 'Q4P2T1R', 'Q4P2T6R', 'Q4P2T8R', 'Q4PD1R', 'Q4PD2R', 'Q4PD3R', 'Q4PD4R',
                    'Q4PD5R', 'Q4PD6R', 'Q4PD7R', 'Q4PD8R', 'Q4PT2R', 'Q4PT3R', 'Q4PT4R', 'Q4PT5R',
                  'Q4PT7R', 'Q5P1T1R', 'Q5P1T6R', 'Q5P1T8R', 'Q5P2T1R', 'Q5P2T6R', 'Q5P2T8R', 'Q5PT2R',
                  'Q5PT3R', 'Q5PT4R', 'Q5PT5R', 'Q5PT7R']

quadlist_short = ['QIT6', 'Q1D', 'Q2D', 'Q3P1T1', 'Q3P1T6', 'Q3P1T8', 'Q3P2T1', 'Q3P2T6', 'Q3P2T8', 'Q3D1',
                    'Q3D2', 'Q3D3', 'Q3D4', 'Q3D5', 'Q3D6', 'Q3D7', 'Q3D8', 'Q3T2', 'Q3T3', 'Q3T4', 'Q3T5',
                    'Q3T7', 'Q4P1T1', 'Q4P1T6', 'Q4P1T8', 'Q4P2T1', 'Q4P2T6', 'Q4P2T8', 'Q4D1', 'Q4D2', 'Q4D3',
                    'Q4D4', 'Q4D5', 'Q4D6', 'Q4D7', 'Q4D8', 'Q4T2', 'Q4T3', 'Q4T4', 'Q4T5', 'Q4T7', 'Q5P1T1',
                    'Q5P1T6', 'Q5P1T8', 'Q5P2T1', 'Q5P2T6', 'Q5P2T8', 'Q5T2', 'Q5T3', 'Q5T4', 'Q5T5', 'Q5T7', ]

short2epics = {short: epics for short, epics in zip(quadlist_short, quadlist_epics)}
epics2short = {epics: short for short, epics in zip(quadlist_short, quadlist_epics)}


