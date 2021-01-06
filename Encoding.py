import numpy as np
from bitarray import bitarray
import zlib
import wave
import sounddevice as sd
import time
import scipy.signal.signaltools as sigtool
import scipy.signal as signal
import sys
from scipy.io.wavfile import write

amplitude = 2000
# time = float(1 / float(sys.argv[1]))
# freq0 = float(sys.argv[2])
# freq1 = float(sys.argv[3])
Fc = 2000  # simulate a carrier frequency of 1kHz
Fbit = 20  # simulated bitrate of data (Original bitrate was 50 and you have changed it)
Fdev = 500  # frequency deviation, make higher than bitrate
N = 6  # how many bits to send
A = 1  # transmitted signal amplitude
Fs = 10000  # sampling frequency for the simulator, must be higher than twice the carrier frequency
A_n = 0.10  # noise peak amplitude
N_prntbits = 10  # number of bits to print in plots
tocode = {
    '0000': '11110',
    '0001': '01001',
    '0010': '10100',
    '0011': '10101',
    '0100': '01010',
    '0101': '01011',
    '0110': '01110',
    '0111': '01111',
    '1000': '10010',
    '1001': '10011',
    '1010': '10110',
    '1011': '10111',
    '1100': '11010',
    '1101': '11011',
    '1110': '11100',
    '1111': '11101'
}

def code4b5b(code):
    output = ""
    while (len(code)):
        output += tocode[code[:4]]
        code = code[4:]
    return output


def codenrz(code):
    output = ""
    prev = 1
    while (len(code)):
        cur = code[:1]
        code = code[1:]
        if (cur == "1"):
            prev = (prev + 1) % 2
        output += str(prev)
    return output


def encoding(to, fromwho, msg):
    output=""
    # print(to, ":", int(to))
    #output = bin(int(fromwho))[2:].zfill(48)
    #output += bin(int(to))[2:].zfill(48)
    #output += bin(len(msg))[2:].zfill(16)
    output=' '.join(format(ord(x), 'b') for x in msg)
    #print("this is output"+output)
    #output=[bin(ord(x))[2:].zfill(8) for x in msg]
    #print("this is output" + output)
   # print(msg[0])
    #for i in range(0, len(msg)):
     #   output += bin(ord(msg[i]))[2:].zfill(8)
    #output += bin(zlib.crc32(bitarray(output).tobytes()) & 0xffffffff)[2:].zfill(32)
    #print("this is code before 4to5"+output)
    #output = code4b5b(output)

    output = codenrz(output)
    output = "0000111110101010101010101010" + output + "10101010101010101010"
    #output = "1010101010101010101010101010101010101010101010101010101010101011" + output
    return output

def generplay(code):
    # frames = [0, 0]
    # frames[0] = np.sin(np.arange(0, 2 * math.pi * time * freq0, 2 * math.pi * freq0 / 44100)) * amplitude
    # frames[1] = np.sin(np.arange(0, 2 * math.pi * time * freq1, 2 * math.pi * freq1 / 44100)) * amplitude
    # with pa.simple.open(direction=pa.STREAM_PLAYBACK, format=pa.SAMPLE_S16LE, rate=44100, channels=1) as player:
    #     for i in code:
    #         player.write(frames[int(i)])
    #         player.drain()


    """
    Data in
    """
    b = " ".join(code)
    c = np.fromstring(b, dtype=int, sep=' ')
    data_in = c
    N = len(data_in)
    # print(type(data_in[0]), type(data_in[5]))
    """
    VCO
    """
    t = np.arange(0, float(N) / float(Fbit), 1 / float(Fs), dtype=np.float)
    # extend the data_in to account for the bitrate and convert 0/1 to frequency
    m = np.zeros(0).astype(float)
    for bit in data_in:
        if bit == 0:
            m = np.hstack((m, np.multiply(np.ones(int(Fs / Fbit)), Fc + Fdev)))
        else:
            m = np.hstack((m, np.multiply(np.ones(int(Fs / Fbit)), Fc - Fdev)))
    # calculate the output of the VCO
    y = np.zeros(0)
    y = A * np.cos(2 * np.pi * np.multiply(m, t))
    waveform_integers = np.int16(y * 32767)
    write("1.wav", Fs, waveform_integers)
    return y


while True:
    try:
        input = input()
    except EOFError:
        break

    if (input == ""):
        break
    else:
        inputspl = input
        # print("inputspl : ", inputspl, int("12"))
        # output = encoding(inputspl[0], inputspl[1], inputspl[2])
        output = encoding('daf','dfsd', inputspl)
        #print("Message input to bits :: ", output)
        print(output)
        y=generplay(output)
        # print(y)
        sd.play(y,Fs)
        time.sleep(7)
    print("Generating completed.")
    break