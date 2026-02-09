function [brx, y, tasa_k] = Transmit_AdaptiveQAM(btx, selected_users, h, M_vector, B)
% Transmite con modulación adaptativa y devuelve la tasa transmitida por usuario
% Inputs:
%   btx: bits transmitidos por cada usuario (K x total_bits)
%   selected_users: vector con el usuario seleccionado en cada trama
%   h: canal Rayleigh (K x num_tramas)
%   M_vector: vector de orden de modulación (1 x num_tramas)
%   B: ancho de banda para calcular la tasa [Mb/s]
% Output:
%   brx: bits transmitidos por cada usuario (K x total_bits)
%   y: la señal recibida
%   tasa_k: tasa transmitida por usuario

K = size(btx, 1);
num_tramas = length(selected_users);

brx = zeros(size(btx));
y = zeros(1, num_tramas);
nb_v = zeros(K, 1);           % bits transmitidos por usuario
bit_count = zeros(K, 1);      % contador total de bits transmitidos

% MODULACIÓN Y TRANSMISIÓN
for n = 1:num_tramas
    m_opt = selected_users(n);
    M = M_vector(n);
    bits_per_sym = log2(M);

    nb = nb_v(m_opt);
    bits = btx(m_opt, (nb+1):(nb+bits_per_sym));
    x_sched = qammod(bits.', M, 'InputType', 'bit');

    y(n) = h(m_opt, n) * x_sched;
    nb_v(m_opt) = nb_v(m_opt) + bits_per_sym;
    bit_count(m_opt) = bit_count(m_opt) + bits_per_sym;
end

% DEMODULACIÓN
nb_v = zeros(K, 1);
for n = 1:num_tramas
    m_sch = selected_users(n);
    M = M_vector(n);
    bits_per_sym = log2(M);

    nb = nb_v(m_sch);
    received_bits = qamdemod(y(n) ./ h(m_sch, n), M, 'OutputType', 'bit');
    brx(m_sch, (nb+1):(nb+bits_per_sym)) = received_bits.';
    nb_v(m_sch) = nb_v(m_sch) + bits_per_sym;
end

% Cálculo de tasa transmitida (bitrate en Mb/s)
duracion_total = num_tramas * 32 / B; % duración en segundos
tasa_k = bit_count / duracion_total / 1e6; % en Mb/s

end
