from fm_tx import *
from fm_rx import *
import Queue
import wave
import Q7interface

##q = Queue.Queue()
##tx_q = q
##rx_q = q

tx_q = Q7interface.tx()
rx_q = Q7interface.rx()

#get the parameters and the data of 1.wav
filepath="/home/sjh/Desktop/FM/1.wav"
wf = wave.open(filepath,'rb')
params = wf.getparams()
data = wf.readframes(params[3])
raw_data = np.fromstring(data,dtype=np.short)

#Transmit threading
FM_Tx = fm_tx(tx_q,params,raw_data)
#FM_Tx.start()

#Receive threading
FM_Rx = fm_rx(rx_q)
FM_Rx.start()
