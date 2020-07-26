function [intensity] = ipx2intensity(IR,Apx, altitude)
%IPX2INTENSITY obtain spectral intensity [W/m2/mic] of light from 
% pixel radiance [W/m2/sr/mic] (vector y)
% Pixel Area     [m^2]  (scalar)
% Sat. Altitude  [m]    (scalar)
%
% IPX2INTENSITY(irradiance, wavelength, pixelArea, altitude)
% irradiance and wavelength vectors must be same length and correspond to
% one antother.

% h = 6.62607015e-34;%  # m2 kg s-1
% c = 299792458; % Light speed                   # m s-1
% wlMKS = wl * 1e-6;
intensity = Apx * (IR) / (altitude^2) ;
end

