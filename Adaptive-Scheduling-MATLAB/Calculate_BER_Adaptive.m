function BER_avg = Calculate_BER_Adaptive(SNR_dB, selected_users)
% Calculate_BER_Adaptive - Calcula la BER esperada usando selección adaptativa.
%   Entradas:
%       SNR_dB         - Matriz SNR instantánea [K x num_tramas]
%       selected_users - Vector con usuario programado por trama
%   Salida:
%       BER_avg - BER media estimada por usuario

[K, N] = size(SNR_dB);
ber_sum = zeros(1, K);   % Suma de BERs por usuario
count = zeros(1, K);     % Número de transmisiones por usuario

for n = 1:N
    k = selected_users(n);                   % Usuario seleccionado
    snr_nat = 10^(SNR_dB(k, n) / 10);        % SNR en unidades naturales

    % Selección de modulación y BER asociada
    M = 64;
    ber = 0.2 * exp(-snr_nat / (M - 1));
    if ber >= 1e-3
        M = 16;
        ber = 0.2 * exp(-snr_nat / (M - 1));
    end

    ber_sum(k) = ber_sum(k) + ber;           % Acumular BER
    count(k) = count(k) + 1;
end

BER_avg = ber_sum ./ max(count, 1);          %Realizar la media
end
