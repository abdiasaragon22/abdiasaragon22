function Pos_MS = Calc_Pos_MS(option, K, lado_x2, lado_y2, lado_x, lado_y)
% Calc_Pos_MS - Calcula la posición de los móviles (MS) según la opción.
% option = 1: Distribución uniforme en un área rectangular (lado_x × lado_y)
% option = 2: Distribución en círculo de radio lado_x2/lado_y2 respecto a la estación base

Pos_MS = []; % Inicializar

if option == 1
    % Opción 1: usuarios uniformemente distribuidos en un área rectangular
    for k = 1:K
        Pos_MS(k) = lado_x* (rand - 0.5) + 1i * lado_y * (rand - 0.5);
    end

elseif option == 2
    % Opción 2: usuarios sobre un círculo (misma distancia al centro)
    Angle_MS = 2 * pi * rand(1, K);
    Pos_MS = lado_x2 * cos(Angle_MS) + 1i * lado_y2 * sin(Angle_MS);

else
    error('La opción elegida no es correcta. Elige entre 1 o 2.');
end

end

