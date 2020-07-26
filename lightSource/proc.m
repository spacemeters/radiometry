aux = dlmread('IRsixS.csv',',',1,0);
IR = aux(:,2);
wl = aux(:,1); % wavelength [mic] == [m*10^-6]  (vector x)
wlMKS = wl * 1e-6; % wavelength [m]

hLEO = 500e3; % 500km low earth orbit
Apx  = (5e3)^2; % 100km squared pixel observed
I = ipx2intensity(IR,Apx,hLEO);

h = 6.62607015e-34;%  # m2 kg s-1
c = 299792458; % Light speed                   # m s-1
photonFlux = I .* wlMKS / h / c;  % [photon/m2/mic]
% Plot
linethick = 1.5;
figure(1)
plot(wl,I,'LineWidth',linethick)
title(sprintf('Intensidad espectral en satélite para A_{px}=%.f m^2',Apx))
ylabel('I [W/m^2]')
xlabel('\lambda [mic]')
figure(2)
plot(wl,photonFlux,'LineWidth',linethick)
title(sprintf('Flujo de fotones en satélite para A_{px}=%.f m^2',Apx))
ylabel('\Phi [photon/m^2/mic]')
xlabel('\lambda [mic]')

% Sensor 
q = 1.60217662e-19; %Fundamental   charge     # Coulomb
Q = 0.9; % quantum efficiency or responsivity. good InGaAs sensors are around 0.9 in IR range
lensDiam = 68e-3; % [m] Gosat has 68mm aperture
Alens = lensDiam^2 * pi / 4;
current = Q * Alens * q * trapz(wl,photonFlux)

return
IRnogas = dlmread('IRsixSNoGas.csv',',',1,0);
% IR(:,1) = 1e4/IR(:,1); % intente pasar todo a wavenumber y no pude
% IRnogas(:,1) = 1e4/IRnogas(:,1);
% plot(IR(:,1),IR(:,2),'LineWidth',linethick)
scatter(IR(:,1),IR(:,2),'.')
hold on
plot(IRnogas(:,1),IRnogas(:,2),'LineWidth',linethick)
title('Irradianza de pixel según presencia de gases contaminantes (6SV)')
ylabel('I_R [W/m2/sr/mic]')
xlabel('\lambda [mic]')
xlim([min(IR(:,1)) max(IR(:,1))])
legend({'6S sin modificar','6S sin CO_2 / CO / N_2O / CH_4'})