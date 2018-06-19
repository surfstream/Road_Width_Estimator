import pyproj

wgs84 = pyproj.Proj(init='epsg:4326')
northFL = pyproj.Proj(init='esri:102660')

def convert_northFL_to_wgs84(easting, northing):
    '''
    Given Easting and Northing for a point, get it's long, lat
    coord.

    Parameters:
        easting: in feet
        northing: in feet

    For easting = 2020000.000 and northing = 533750.000,
    the output will be (-84.33654615255946, 30.467551137914395) 
    '''
    return pyproj.transform(northFL, wgs84,
                            easting * 0.3048, northing * 0.3048)

def convert_wgs84_to_northFL(lon, lat):
    '''
    '''
    x, y = pyproj.transform(wgs84, northFL, lon, lat)
    return x / 0.3048, y / 0.3048

