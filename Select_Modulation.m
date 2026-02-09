function M = Select_Modulation(SNR_dB)
% Select_Modulation - Selecciona entre 64QAM y 16QAM según SNR y BER objetivo.
%   Entrada:
%       SNR_dB - Valor de SNR instantanea en dBs para un usuario en una trama
%   Salida:
%       M - Orden de modulación seleccionado (64 o 16)

snr_lin = 10^(SNR_dB / 10);  % Convertimos la SNR de dB a lineal

% Primero probamos con 64QAM
M = 64;
ber = 0.2 * exp(-snr_lin / (M - 1));  % Fórmula aproximada de BER

% Si no se alcanza la BER deseada (<10^-3), bajamos a 16QAM
if ber >= 1e-3
    M = 16;
end

end
