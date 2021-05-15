import warnings
warnings.filterwarnings('ignore')
import sys
import os
from astroquery.skyview import SkyView
from astropy.coordinates import SkyCoord
import astropy.units as u
import aplpy
import matplotlib.pyplot as plt
from astropy.io import fits
import astropy

def coords_from_name(field_name):
    """Get ra, dec coordinates from a field name using astropy
    Args:
        field_name (str): Field name, e.g. 'M101'
    Returns:
        (float, float): ra, dec in degrees
    Example:
        >>> coords_from_name('M101')
        (210.80242917, 54.34875)
    """
    coords = SkyCoord.from_name(field_name)
    return coords

def call_skyview_simple(survey, source_name, fov=1):
    """Call Skyview to download data from a survey based on input parameters
    Args:
        survey (str): name of survey, from https://skyview.gsfc.nasa.gov/current/cgi/survey.pl
        source (str): name of astronomical source
        fov (float): FOV in degrees
    Examples:
        >>> call_skyview('DSS', 'M31', 2.)
        >>> call_skyview('NVSS', NGC6670, 0.5)
    """
    coords = coords_from_name(source_name)
    outname = f'{source_name}_{survey}_{fov}d.fits'
    images = SkyView.get_images(coords, survey,
                                coordinates='J2000',
                                projection='Car', pixels=500,
                                height=fov*u.deg, width=fov*u.deg)
    fitsname = f'images/{source_name}_{survey}_{fov}d.fits'
    try:
        images[0][0].writeto(fitsname, overwrite=True)
    except astropy.io.fits.verify.VerifyError:
        print('Data not available')
        pass
    return fitsname 

def plot_fits(fits_name, plot_title=None, cmap_name='viridis', colorbar=True, contour=True):
    """Make a PNG plot out of a FITS file
    
    Args:
        fits_name (str): path of fits file
        plot_title (str): plot title, default is name of the fits file
        cmap_name (str): name of colormap, default is viridis
        colorbar (bool): include colorbar, default is True
        contour (bool): include contour, default is True
    """
    f = aplpy.FITSFigure(fits_name, figsize=(10, 8))
    if plot_title == None:
        plot_title = fits_name.replace('.fits', '')
    plt.title(plot_title)
    f.show_colorscale(cmap=cmap_name, stretch='linear')
    f.ticks.set_color('k')
    if colorbar:
        f.add_colorbar()
    if 'BMAJ' in fits.open(fits_name)[0].header:
        f.add_beam()
        print(f'Adding beam for {fits_name}')
    if contour:
        f.show_contour()
    output_name = fits_name.replace('.fits', '.png')
    plt.savefig(output_name, dpi=200, bbox_inches='tight')

def main_func(source_name, survey, fov):
    if not os.path.isdir('images'):
        os.mkdir('images')
    fitsname = call_skyview_simple(survey, source_name, fov)
    plot_fits(fitsname, plot_title=None, cmap_name='viridis', colorbar=True)

if __name__ == '__main__':
    #warnings.filterwarnings('ignore', category=AstropyDeprecationWarning, append=True)
    #warnings.simplefilter('ignore', AstropyDeprecationWarning)
    main_func(sys.argv[1], sys.argv[2], float(sys.argv[3]))
