function SNR_dB = calcular_SNRs(Pos_BS, Pos_MS, Ptx, B, f, sigma_sh, N0)
% Calcula la SNR para cada usuario considerando el path loss, shadowing, y Rayleigh fading.
%
% Inputs:
%   Pos_BS    - Posición de la estación base
%   Pos_MS    - Posiciones de los usuarios (vector)
%   Ptx       - Potencia de transmisión
%   B         - Ancho de banda del canal
%   f         - Frecuencia en Hz
%   sigma_sh  - Desviación estándar para el shadowing log-normal
%   N0        - Densidad espectral de ruido (W/Hz)
%
% Output:
%   SNR_dB    - SNR en dB para cada usuario

    K = length(Pos_MS);              % Número de usuarios
    SNR_dB = zeros(1, K);            % Vector para almacenar la SNR en dB

    % Calculamos la potencia total de ruido (W)
    Noise = B * N0;   

    % Calculamos la distancia entre la estación base y los usuarios
    dist_BS_MS = abs(Pos_MS - Pos_BS);
    
    % Calculamos Path Loss en dB
    PL = 32.4 + 20*log10(f / 1e9) + 37.6 * log10(dist_BS_MS);       % Path loss en dB
    pl = 10.^(PL / 10);                                              % Path loss en unidades naturales

    % Calculamos la potencia recibida media (en dB)
    Prx_dB = 10*log10(Ptx) - PL;                                      % Potencia recibida media en dB

    % Aplicamos shadowing log-normal
    Prx_dB = Prx_dB + sigma_sh * randn(1, K);                          % Potencia recibida (dB) aplicando shadowing

    % Calculamos la SNR (en dB) sin Rayleigh fading
    SNR_dB = Prx_dB - 10 * log10(Noise);                             % SNR en dB
end