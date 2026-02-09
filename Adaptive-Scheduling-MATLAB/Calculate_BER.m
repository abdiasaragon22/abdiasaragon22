function BER_avg = Calculate_BER(SNR_instantanea, M)
% Calculate_BER - Calcula la BER media utilizando la fórmula especificada.
%   SNR_instantanea - Matriz de SNRs instantáneas [dB], de tamaño K x Num_tramas
%   M               - Orden de la modulación (e.g., 16 para 16-QAM, 64 para 64-QAM)


% Convertir SNR de dB a unidades naturales
SNR_nat = 10.^(SNR_instantanea / 10);

% Calcular la BER instantánea usando la fórmula dada
BER_instantanea = 0.2 * exp(-SNR_nat / (M - 1));

% Calcular la BER media para cada usuario
BER_avg = mean(BER_instantanea, 2);

end
