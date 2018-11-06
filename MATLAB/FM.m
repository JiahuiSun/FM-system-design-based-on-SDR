clear
close all
%% Load the data
test_data = 's11.wav';     
[data, FS] = audioread(test_data);
data = data.'*50;
% sound(data, FS);
t = linspace(0, (length(data)-1)/FS, length(data));
% t = 0:1/FS:(length(data)-1)/FS;
f = linspace(-FS/2, FS/2, length(data));
figure;
subplot(2,1,1); plot(t,data);
xlabel('t/s'); ylabel('Amp');
subplot(2,1,2); plot(f, fftshift(abs(fft(data))));
xlabel('f/Hz'); ylabel('H(¦¸)');
%% Modulation
fc = 0;
Kf = 10;
cum_data = cumsum(data) / FS; 
mod_data = cos(2*pi*fc*t + Kf*cum_data )+1j*sin(2*pi*fc*t+Kf*cum_data);
%% Upsampling
fs = 1.92e6; 
osr = fs/FS;
interp_t = 0:1/fs:(length(data)-1)/FS;
% interp_data = interp1(t,mod_data,interp_t);
interp_data = resample(mod_data,osr,1);
%% Send and add noise
snr = 30;
noise_data = awgn(interp_data,snr);
%% downsampling
% down_data = decimate(interp_data,osr);
% down_data = downsample(interp_data,osr);
% down_data = resample(interp_data,1,osr);
down_data = resample(noise_data,1,osr);
%% Design LPF using FIR
p = 3e3; s = 3.5e3;
wp = 2*pi*p/FS;
ws = 2*pi*s/FS;
wc = (ws+wp)/2/pi;
Bt = ws-wp;
N = ceil(6.6*pi/Bt);
hn = fir1(N-1,wc);
figure;
stem(0:(N-1),hn,'rd');grid on;hold on
figure;
freqz(hn,1,FS); grid on; hold on
% filter_data = filter(hn,1,down_data);
filter_data = upfirdn(down_data,hn);
%% Demodulation 
% demod_data = unwrap(diff(angle(down_data)))*1e4;
demod_data = unwrap(diff(angle(filter_data)))*1e4;
disp('SoundCard Output @ 16 KHz')
sound(demod_data,FS);


