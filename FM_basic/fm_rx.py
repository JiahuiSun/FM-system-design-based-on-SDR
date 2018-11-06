import numpy as np
import pyaudio
import threading
from scipy import signal
from ctypes import *
C_lib = CDLL("./C_lib.so")

class fm_rx(threading.Thread):
    def __init__(self,rx_q):
        threading.Thread.__init__(self)
        self.rx_q = rx_q

    def run(self):
        #set the params
        SDR_RATE = 1.92e6
        DOWN_FACTOR = 120
        CHANNELS = 1
        AUDIO_RATE = int(SDR_RATE/DOWN_FACTOR)
        FORMAT = pyaudio.paInt16
        AUDIO_SIZE = 320

        #set the audio stream
        p = pyaudio.PyAudio()
        print("SoundCard Output @ %d KHz" % (AUDIO_RATE/1e3))
        stream = p.open(format = FORMAT,
                        channels = CHANNELS,
                        rate = AUDIO_RATE,
                        output = True)
        #allocate space for rx_data
        input_sample_len = AUDIO_SIZE*DOWN_FACTOR
        pInput_real = (c_double*input_sample_len)()
        pInput_imag = (c_double*input_sample_len)()
        
        data_rx = np.empty(input_sample_len, dtype = complex)
##        b,a = signal.iirdesign(7./8,7.8/8,1,40)
##        FIR_LPF = signal.firwin(1,2*4e3/AUDIO_RATE)
        FIR_LPF = signal.firwin(2,1/(AUDIO_RATE/2.))
        while True:
            data_buf = self.rx_q.get(input_sample_len*4)
            ok_separater = C_lib.CSM_data_separater(data_buf,pInput_real,pInput_imag,input_sample_len)
            #The np array shares the memory with the ctypes object
            data_rx.real = np.ctypeslib.as_array(pInput_real).astype(np.int16)
            data_rx.imag = np.ctypeslib.as_array(pInput_imag).astype(np.int16)
            
            #decimation
            dec_data = signal.decimate(data_rx,DOWN_FACTOR,ftype='fir')

            #LPF
##            dec_data_out = signal.lfilter(b,a,dec_data)
##            dec_data_out = signal.lfilter(FIR_LPF,1.0,dec_data)            
            dec_data_out = signal.fftconvolve(FIR_LPF,dec_data)

            #demodulation
            demod_data = np.unwrap(np.diff(np.angle(dec_data_out)))*1e4
            play_data = demod_data.astype(np.int16).tostring()

##            data_delay = np.insert(dec_data_out,0,pre_data)
##            pre_data = data_delay[-1]
##            data_delay = np.delete(data_delay,-1)
##            diff_data = dec_data_out*np.conj(data_delay)
##            ang_data = np.angle(diff_data)
##            audio_data = np.unwrap(ang_data)*1e4
##            play_data = audio_data.astype(np.int16).tostring()            
            stream.write(play_data)
        stream.close()
        p.terminate()
