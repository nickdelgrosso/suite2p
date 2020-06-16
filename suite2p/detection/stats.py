import numpy as np

from suite2p.detection import masks, utils


def mean_r_squared(y, x, estimator=np.median):
    return np.mean(np.sqrt((y - estimator(y)) ** 2 + ((x - estimator(x)) ** 2)))


def roi_stats(ops, stat):
    """ computes statistics of ROIs

    Parameters
    ----------
    ops : dictionary
        'aspect', 'diameter'

    stat : dictionary
        'ypix', 'xpix', 'lam'

    Returns
    -------
    stat : dictionary
        adds 'npix', 'npix_norm', 'med', 'footprint', 'compact', 'radius', 'aspect_ratio'

    """
    if 'aspect' in ops:
        d0 = np.array([int(ops['aspect']*10), 10])
    else:
        d0 = ops['diameter']
        if isinstance(d0, int):
            d0 = [d0,d0]

    rs = masks.circle_mask(np.array([30, 30]))
    rsort = np.sort(rs.flatten())

    ncells = len(stat)
    mrs = np.zeros((ncells,))
    for k in range(0,ncells):
        stat0 = stat[k]
        ypix, xpix, lam = stat0['ypix'], stat0['xpix'], stat0['lam']

        # compute compactness of ROI
        mrs_val = mean_r_squared(y=ypix, x=xpix)
        mrs[k] = mrs_val
        stat0['mrs'] = mrs_val
        stat0['mrs0'] = np.mean(rsort[:ypix.size])
        stat0['compact'] = stat0['mrs'] / (1e-10+stat0['mrs0'])
        stat0['med'] = [np.median(stat0['ypix']), np.median(stat0['xpix'])]
        stat0['npix'] = xpix.size

        if 'footprint' not in stat0:
            stat0['footprint'] = 0
        if 'med' not in stat:
            stat0['med'] = [np.median(stat0['ypix']), np.median(stat0['xpix'])]
        if 'radius' not in stat0:
            radius = utils.fitMVGaus(ypix / d0[0], xpix / d0[1], lam, 2)[2]
            stat0['radius'] = radius[0] * d0.mean()
            stat0['aspect_ratio'] = 2 * radius[0]/(.01 + radius[0] + radius[1])

    npix = np.array([stat[n]['npix'] for n in range(len(stat))]).astype('float32')
    npix /= np.mean(npix[:100])

    mmrs = np.nanmedian(mrs[:100])
    for n in range(len(stat)):
        stat[n]['mrs'] = stat[n]['mrs'] / (1e-10+mmrs)
        stat[n]['npix_norm'] = npix[n]
    stat = np.array(stat)

    return stat