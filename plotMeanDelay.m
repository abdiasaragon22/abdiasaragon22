function plotMeanDelay(retardos)
% plotMeanDelay – Calcula y dibuja el retardo medio (en tramas) por usuario.
%
% Input:
%   retardos – cell array 1×K donde cada elemento es el vector de retardos
%               (“número de tramas esperadas”) registrados para ese usuario
%
%   plotMeanDelay(retardos);

    K = numel(retardos);
    meanDelay = zeros(1, K);
    for u = 1:K
        if isempty(retardos{u})
            meanDelay(u) = NaN;  % Usuario nunca seleccionado
        else
            meanDelay(u) = mean(retardos{u});
        end
    end

    figure;
    bar(1:K, meanDelay);
    xlabel('Usuario');
    ylabel('Retardo medio [tramas]');
    title('Retardo medio hasta volver a transmitir por usuario');
    grid on;
end
