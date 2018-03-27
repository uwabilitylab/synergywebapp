def xycoordinates(x, y, f):

    coordinates = {
        'raw':[],
        'filt':[]
    }
    for i,row in enumerate(x):

        coordinates['raw'].append({
            'x':row,
            'y':y[i]
        })
        coordinates['filt'].append({
            'x':row,
            'y':f[i]
        })

    return coordinates
