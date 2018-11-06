import numpy as np
import threading
from ctypes import *
C_lib = CDLL("./C_lib.so")

class fm_tx(threading.Thread):
    #Run immediately when an object of the class is created to initialize
    def __init__(self,tx_q,params,raw_data):
        threading.Thread.__init__(self)
        self.tx_q = tx_q
        self.params = params
        self.raw_data = raw_data

    def run(self):
        #set the params
        sample_rate = self.params[2]#16KHz
        sample_num = self.params[3]#280248
        SDR_RATE = 1.92e6
        FRAME_DURATION = 20e-3#the length of one frame
        
        osr = int(SDR_RATE/sample_rate)#over sample rate
        frame_len = sample_rate * FRAME_DURATION#The amount of data in one frame 
        frame_num = int(sample_num/frame_len)#frames numbers of the whole file
        frame_len = int(frame_len)
        
        #allocate space for tx_data
        interp_output_len = frame_len*osr
        fp_real_buf = (c_short*interp_output_len)()
        fp_imag_buf = (c_short*interp_output_len)()

        #modulation
        mf=5
        fc=0
        cum_data = np.cumsum(self.raw_data)/float(sample_rate)#integral
        t = np.linspace(0,sample_num-1,sample_num)
        interp_t = np.linspace(0,frame_len-1,frame_len*osr)
        mod_data = np.cos(mf*cum_data+2*np.pi*t*fc)+1j*np.sin(mf*cum_data+2*np.pi*t*fc)

        #fix point and move eleven bits to the left and turn into int16
        fp_mod_data_real = np.int16(mod_data.real*2048)
        fp_mod_data_imag = np.int16(mod_data.imag*2048)

        #put each frame into buffer
        for frm_idx in range(frame_num):
            fp_buf = (c_short*(interp_output_len*2))()#both real and imag
            
            #interpolation    
            fp_real_buf[:] = np.interp(interp_t,t[:frame_len],fp_mod_data_real[frm_idx*frame_len:(frm_idx+1)*frame_len]).astype(np.int16)
            fp_imag_buf[:] = np.interp(interp_t,t[:frame_len],fp_mod_data_imag[frm_idx*frame_len:(frm_idx+1)*frame_len]).astype(np.int16)

            #combine real and image to one and put into queue
            of_combiner = C_lib.CSM_data_combiner(fp_real_buf,fp_imag_buf,fp_buf,interp_output_len)
            self.tx_q.put(fp_buf)
