function [brx, y] = Transmit_16QAM(btx, selected_users, h, M)
% Transmit_16QAM - Transmite información usando 16QAM basado en los usuarios seleccionados.
%   btx           - Matriz de bits a transmitir (K x num_bits)
%   selected_users - Vector de usuarios seleccionados para cada trama (longitud num_tramas)
%   h             - Canal Rayleigh (K x num_tramas)
%   M             - Orden de la modulación (16 para 16QAM)

K = size(btx, 1);
num_tramas = length(selected_users);

% Inicializar variables
brx = zeros(size(btx));  % Bits recibidos
y = zeros(1, num_tramas);  % Señal transmitida
nb_v = zeros(K, 1);  % Contador de bits transmitidos por usuario

% MODULACIÓN Y TRANSMISIÓN
for n = 1:num_tramas
    % Identificar el usuario que transmite
    m_opt = selected_users(n);

    % Modular los bits del usuario seleccionado
    nb = nb_v(m_opt);
    bits = btx(m_opt, (nb+1):(nb+4));
    x_sched = qammod(bits.', M, 'InputType', 'bit');

    % Transmitir a través del canal
    y(n) = h(m_opt, n) * x_sched;

    % Actualizar el contador de bits
    nb_v(m_opt) = nb_v(m_opt) + 4;
end

% DEMODULACIÓN
nb_v = zeros(K, 1);  % Reiniciar el contador de bits
for n = 1:num_tramas
    % Identificar el usuario que transmitió
    m_sch = selected_users(n);

    % Demodular los bits recibidos
    nb = nb_v(m_sch);
    received_bits = qamdemod(y(n) ./ h(m_sch, n), M, 'OutputType', 'bit');
    brx(m_sch, (nb+1):(nb+4)) = received_bits.';

    % Actualizar el contador de bits
    nb_v(m_sch) = nb_v(m_sch) + 4;
end

end
