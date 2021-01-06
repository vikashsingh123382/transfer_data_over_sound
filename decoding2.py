from scipy.io.wavfile import write
from scipy.io import wavfile
import sounddevice as sd
import numpy as np
import scipy.signal.signaltools as sigtool
import scipy.signal as signal
import time

fs = 10000  # Sample rate
Fc = 1000  # simulate a carrier frequency of 1kHz
Fbit = 20  # simulated bitrate of data (Earlier it was 50)
Fdev = 500  # frequency deviation, make higher than bitrate
N = 64  # how many bits to send
A = 1  # transmitted signal amplitude
Fs = 10000  # sampling frequency for the simulator, must be higher than twice the carrier frequency
A_n = 0.1  # noise peak amplitude
N_prntbits = 10

todecode = {
    '11110':'0000',
    '01001':'0001',
    '10100':'0010',
    '10101':'0011',
    '01010':'0100',
    '01011':'0101',
    '01110':'0110',
    '01111':'0111',
    '10010':'1000',
    '10011':'1001',
    '10110':'1010',
    '10111':'1011',
    '11010':'1100',
    '11011':'1101',
    '11100':'1110',
    '11101':'1111'
}

def recording():
    seconds = 8  # Duration of recording
    print("start")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    write('output.wav', fs, myrecording)
    print("end")



#print("this is after transfer"+rx_data)
# (nchannels, sampwidth, sampformat, framerate) = (1, 2, pa.SAMPLE_S16LE, 44100)

"""
def dominatfreq(time, recorder):
	nframes = int(float(time)*recorder.rate)
	tab = recorder.read(nframes)
	if (len(tab) == 0):
		return -1
	halftab = np.fft.fft(tab)[0:int(time*recorder.rate/2)]
	return (np.argmax(np.absolute(halftab))/time)
  """
def decodenrz(code):
	prev = 1
	output = ""
	while (len(code)):
		cur = int(code[:1])
		code = code[1:]
		if (cur != prev):
			output += "1"
		else:
			output += "0"
		prev = cur
	return output

def decode4b5b(code):
	count = 5
	output = ""
	while(count <= len(code)):
		output += todecode[code[count-5:count]]
		count += 5
	return output

def decode(code):
    output = decodenrz(code)
    #print("code after decode nrz"+out)
    #output = decode4b5b(out)
    #print("this is code"+output)
    count=0
    output5=""
    while(count<len(output)):
        output5+='0'
        output5+=output[count:count+7]
        output5+=' '
        count+=8
    ascii_string = ""
    binary_values = output5.split()
    for binary_value in binary_values:
        an_integer = int(binary_value, 2)
        ascii_character = chr(an_integer)
        ascii_string += ascii_character
    #print(ascii_string)

    #print(output5)
    #print(output[48:96])
    #output1 = str(int(output[48:96], 2)) + " "
    #print("this is "+output1)
    #output1 += str(int(output[:48], 2)) + " "
    #print("this is " + output1)
    #endofmsg = 112 + 8 * int(output[96:112], 16)  # 112i dl
    #output1 += ('%x' % int(output[112:endofmsg], 16)).decode('hex').decode('utf-8')
    return ascii_string

def main_program():
    samplerate, data = wavfile.read('1.wav')
    y = data
    print(y)

    # sd.play(y, Fs)

    """
    Noisy Channel
    """
    #create some noise
    noise = (np.random.randn(len(y))+1)*A_n
    snr =10*np.log10(np.mean(np.square(y)) / np.mean(np.square(noise)))
    print ("SNR = %fdB",snr)
    y=np.add(y,noise)

    y_diff =np.diff(y,1)
    y_env = np.abs(sigtool.hilbert(y_diff))
    h=signal.firwin(numtaps=100, cutoff=Fbit*2, nyq=Fs/2)
    y_filtered=signal.lfilter(h, 1.0, y_env)

    #view the data after adding noise
    N_FFT = float(len(y_filtered))
    f = np.arange(0,Fs/2,Fs/N_FFT)
    w = np.hanning(len(y_filtered))
    y_f = np.fft.fft(np.multiply(y_filtered,w))
    y_f = 10*np.log10(np.abs(y_f[0:int(N_FFT/2)]/N_FFT))
    # print("data", y)

    """
    slicer
    """
    # calculate the mean of the signal
    mean = np.mean(y_filtered)
    # if the mean of the bit period is higher than the mean, the data is a 0

    rx_data = ""
    sampled_signal = y_filtered[int(Fs / Fbit / 2):len(y_filtered):int(Fs / Fbit)]

    for bit in sampled_signal:
        if bit > mean:
            rx_data += '0'
        else:
            rx_data+='1'

    print(rx_data, type(rx_data))

    # rx_data = "111111111111111010101010101010101001100000100011001001000010010000100101010101010101010101010111111111"
    k = 0
    j = 0
    len_rx_data = len(rx_data)
    code = ''

    added_string_front1 = "10101010101010101010"

    for i in range(0, len_rx_data-20):
        a = rx_data[i:i+20]
        if a == added_string_front1:
            k = i+20
            break

    added_string = "10101010101010101010"
    for i in reversed(range(len_rx_data)):
        a = rx_data[i-19:i+1]
        if a == added_string:
            j = i-19
            break

    print(k, j)
    code = rx_data[k:j]
    print(code)

    outpu = decode(code)
    # outpu = decode(rx_data)
    print("message output to bits")
    print(outpu)
    # outpu="yashwant"
    return outpu

# time.sleep(5)

# 000011111010101010101010101001100000100011001001000010010000100101010101010101010101010
#  00011111010101010101010101001100000100011001001000010010000100101010101010101010101010

# recording()
# main_program()