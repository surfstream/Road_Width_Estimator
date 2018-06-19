from osgeo import gdal, osr
import subprocess
import re
import numpy

def get_geotiff_bbox(tiff_img):
    """
    Use gdal library to extract bounding box info regarding a geotiff image.

    Portion of output produced by gdalinfo that we are interested in:
      Command:
          gdalinfo <tiff_image>

      Output:
          ...
          Lower Left  ( 2018750.000,  533750.000) 
          Upper Right ( 2020000.000,  535000.000) 
          ...
    """
    # Get tiff info
    cmd = ['gdalinfo', tiff_img]
    tiff_info = subprocess.check_output(cmd).decode("utf-8")

    # Parse and extract the longitudes and latitudes
    patc = re.compile(r"(?:Lower Left|Upper Right).*?(\d+\.\d+),\s+(\d+\.\d+).*")
    low_left, up_right = patc.findall(tiff_info)

    return [float(v) for v in low_left + up_right]


def get_pixel_for_point(geomat, x, y):
    """
    Given GeoTransform data and geographic coordinates x, y,
    return the pixel position in row, col.

    https://pcjericks.github.io/py-gdalogr-cookbook/

    Args:
        geomat:
            gdal.Open("img.tif").GetGeoTransform())
        x, y:
            latitude, longitude
    """
    ulX = geomat[0]        # upper left corner X
    ulY = geomat[3]        # upper left corner Y
    xDist = geomat[1]      # pixel width
    yDist = geomat[5]      # pixel height
    rtnX = geomat[2]       
    rtnY = geomat[4]


    col = int((x - ulX) / xDist)
    row = int((y - ulY) / yDist)

    return row, col


def get_point_for_pixel(geomat, x_offset, y_offset):
    """
    Given the pixel offsets along the x and y directions and
    the geotransform matrix, return its corresponding
    geographic coordinate.
    """
    origin_X = geomat[0]
    origin_Y = geomat[3]
    pix_width = geomat[1]
    pix_height = geomat[5]
    Xgeo = origin_X + pix_width * x_offset
    Ygeo = origin_Y + pix_height * y_offset

    return Xgeo, Ygeo


def get_geotiff_info(tiff_img):
    gtif = gdal.Open(tiff_img)
    tiff_size = (gtif.RasterXSize, gtif.RasterYSize)
    geomat = gtif.GetGeoTransform()

    return tiff_size, geomat


def save_array_as_geotiff_img(bands, orig_tiff, out_fname):
    """
    Create a new Geotiff image using input list of bands
    with project information from input tiff image.

    Args:
        bands: list of numpy arrays
            If len(bands) == 1, it's a Gray channel.
            If len(bands) == 3, it has R, G, B channels.

        orig_tiff: string with existing tiff image filename

        out_fname: string with output tiff image filename

    Reference:
    https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html#create-raster-from-array
    """
    rows, cols = bands[0].shape

    # Create new
    driver = gdal.GetDriverByName('GTiff')
    dest_raster = driver.Create(out_fname, cols, rows, len(bands), gdal.GDT_Byte)

    # Get geomat from original
    src = gdal.Open(orig_tiff)
    geomat = src.GetGeoTransform()
    dest_raster.SetGeoTransform(geomat)

    # Get and set projection info
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(src.GetProjectionRef())
    dest_raster.SetProjection(raster_srs.ExportToWkt())

    # Write each band
    for i, band in enumerate(bands):
        dest_raster.GetRasterBand(i + 1).WriteArray(band)

    dest_raster.FlushCache()


def test_pixel_translation():
    """
    For the image: ../lasfiles/tr4/tr4_sat.tif

    Corner Coordinates:
        Upper Left  ( 2045000.000,  516250.000)
        Lower Left  ( 2045000.000,  515000.000)
        Upper Right ( 2046250.000,  516250.000)
        Lower Right ( 2046250.000,  515000.000)
        Center      ( 2045625.000,  515625.000)

    For "../lasfiles/46135_0/46135_0.tif":
        Upper Left  ( 2020000.000,  542500.000) 
        Lower Left  ( 2020000.000,  540000.000) 
        Upper Right ( 2022500.000,  542500.000) 
        Lower Right ( 2022500.000,  540000.000) 
        Center      ( 2021250.000,  541250.000) 
    """
    # First test
    tiff_img = "../lasfiles/tr4/tr4_sat.tif"
    gtif = gdal.Open(tiff_img)
    geomat = gtif.GetGeoTransform()

    r, c = 0, 0
    x, y = get_point_for_pixel(geomat, r, c)
    print(x, y)
    rr, cc = get_pixel_for_point(geomat, x, y)
    print(rr, cc)

    r, c = 2500, 2500
    x, y = get_point_for_pixel(geomat, r, c)
    assert((( 2046250.000,  515000.000)) == (x, y))

    x, y = 2045625.000,  515625.000
    x, y = 2045000.000,  515625.000
    rr, cc = get_pixel_for_point(geomat, x, y)
    print(rr, abs(cc))

    # Second test
    tiff_img = "../lasfiles/46135_0/46135_0.tif"
    gtif = gdal.Open(tiff_img)
    geomat = gtif.GetGeoTransform()
    print(geomat)
    ulX = geomat[0]        # upper left corner X
    ulY = geomat[3]        # upper left corner Y
    xDist = geomat[1]      # pixel width
    yDist = geomat[5]      # pixel height

    print(ulX, ulY, xDist, yDist)

if __name__ == "__main__":
    test_pixel_translation()
