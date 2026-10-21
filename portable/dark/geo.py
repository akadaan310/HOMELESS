"""§16 [K]: WGS84 ellipsoid-height ECEF and local ENU, binary64 meters.
No orthometric conversion, tiles, terrain or source reconstruction is implied.
"""
import math
A = 6378137.0
F = 1 / 298.257223563
E2 = F * (2 - F)


def ecef(latitude, longitude, ellipsoid_height):
    if not all(math.isfinite(v) for v in (latitude, longitude, ellipsoid_height)) or not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError('finite WGS84 degrees and ellipsoid meters required')
    p, l = math.radians(latitude), math.radians(longitude)
    n = A / math.sqrt(1 - E2 * math.sin(p) ** 2)
    return ((n + ellipsoid_height) * math.cos(p) * math.cos(l),
            (n + ellipsoid_height) * math.cos(p) * math.sin(l),
            (n * (1 - E2) + ellipsoid_height) * math.sin(p))


def basis(anchor):
    ecef(*anchor)  # validate datum coordinates
    p, l = map(math.radians, anchor[:2])
    return ((-math.sin(l), math.cos(l), 0),
            (-math.sin(p)*math.cos(l), -math.sin(p)*math.sin(l), math.cos(p)),
            (math.cos(p)*math.cos(l), math.cos(p)*math.sin(l), math.sin(p)))


def enu(point, anchor):
    if len(point) != 3 or not all(math.isfinite(v) for v in point):
        raise ValueError('finite ECEF point required')
    delta = tuple(x - y for x, y in zip(point, ecef(*anchor)))
    return tuple(sum(x*y for x,y in zip(row,delta)) for row in basis(anchor))


def unenu(local, anchor):
    if len(local) != 3 or not all(math.isfinite(v) for v in local):
        raise ValueError('finite local point required')
    rows = basis(anchor)
    return tuple(ecef(*anchor)[j] + sum(rows[i][j]*local[i] for i in range(3)) for j in range(3))
