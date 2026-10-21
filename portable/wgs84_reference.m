% §§16,55,87: independent Octave double precision WGS84 numeric fixture.
% Input columns latitude degrees, longitude degrees, ellipsoid meters.
args = argv();
p = dlmread(args{1}, ',');
a = 6378137; f = 1/298.257223563; e2 = f*(2-f);
lat = p(:,1)*pi/180; lon = p(:,2)*pi/180; h = p(:,3);
n = a ./ sqrt(1-e2*sin(lat).^2);
x = (n+h).*cos(lat).*cos(lon);
y = (n+h).*cos(lat).*sin(lon);
z = (n*(1-e2)+h).*sin(lat);
dlmwrite(args{2}, [x,y,z], 'precision', '%.17g');
