function SNR_instantanea = Apply_Rayleigh_Channel(SNR_dB, fd, num_muestras, ts)
% Apply_Rayleigh_Channel - Aplica el canal Rayleigh y devuelve la SNR instantánea.
%   SNR_dB        : vector de SNR medias en dB (K×1)
%   fd            : frecuencia Doppler en Hz
%   num_muestras  : número total de muestras a simular
%   ts            : período de muestreo (s)
%
% Salida:
%   SNR_instantanea : matriz K×num_muestras con la SNR instantánea en dB
%                     para cada usuario en cada una de las num_muestras.

  K = length(SNR_dB);
  SNR_instantanea = zeros(K, num_muestras);

  for n = 1:K
    % 1) SNR media en unidades naturales
    snr_nat = 10^(SNR_dB(n) / 10);

    % 2) Creamos el canal Rayleigh
    ch = comm.RayleighChannel( ...
        'SampleRate', 1/ts, ...
        'MaximumDopplerShift', fd, ...
        'PathGainsOutputPort', true);

    % 3) Generamos num_muestras ganancias complejas H
    [~, H] = ch( ones(num_muestras, 1) );  % H es num_muestras×1

    % 4) Escalamos H por sqrt(snr_linear): h(n,:) es 1×num_muestras
    h(n, :) = (sqrt(snr_nat) * H.').';  

    % 5) Calculamos SNR instantánea en dB = 10·log10(|h(n,j)|^2)
    SNR_instantanea(n, :) = 10 * log10( abs(h(n, :)).^2 );
  end
end
