# libraries
import wave
import struct
from scipy import signal
import pyaudio
import numpy as np
import math
import sys
import glob

def clip16( x ):    
    # Clipping for 16 bits
    if x > 32767:
        x = 32767
    elif x < -32768:
        x = -32768
    else:
        x = x        
    return int(x)


#Music
if len(sys.argv) == 1:
	print('We have the following music:')
	for file in glob.glob("*.wav"):
		print(file)
	filename = raw_input('Enter the music filename you want to play: ')
else:
    filename = sys.argv[1]


#Gain
Glib = [[1 for i in range(10)] for j in range(7)]
Glib[0][:]=[+6, +4, -5, +2, +3, +4, +4, +5, +5, +6]
Glib[1][:]=[+6, +4, 0, -2, -6, +1, +4, +6, +7, +9]
Glib[2][:]=[+4, 0, +1, +2, +3, +4, +5, +4, +3, +3]
Glib[3][:]=[-3, -3, 0, +2, +3, +3, +3, +2, +1, +1]
Glib[4][:]=[-3, -1, -1, 0, -1, +1, +4, +3, +4, 0]
Glib[5][:]=[+4, +2, 0, -3, -6, -6, -3, 0, +3, +5]
Gain=[0 for i in range(10)]
ty=input ("Please choose the model:\n1.Bass\n2.Rock\n3.Vocal\n4.Pop\n5.Classic\n6.Special\n")

if ((ty != 6) and (ty != 1) and (ty != 2) and (ty !=3) and (ty!= 4) and (ty!= 5)):
	y_n = input('Do you want to set the Equalizer by youself?(Enter 1 for yes, 2 for no)')

	if y_n == 2:
	    ty = input('Enter the mode number you want to play:')
	else:    
		print "Enter ten numbers you want to set for the Equalizer: (for example: 2 3 -5 -8 ...)"
        numbers = raw_input()
        Glib[6][:] = map(int, numbers.split())
        ty=7
Gain = [10**(Glib[ty-1][n]/20.0) for n in range(10)]

#Play        
print(filename ,"is playing")
wf = wave.open(filename,'rb')
Fs = wf.getframerate()
WIDTH = wf.getsampwidth()
LEN = wf.getnframes()
CHANNELS = wf.getnchannels()

#print 'The sampling rate is {0:d} samples per second'.format(Fs)
#print 'Each sample is {0:d} bytes'.format(WIDTH)
#print 'The signal is {0:d} samples long'.format(LEN)
#print 'The signal has {0:d} channel(s)'.format(CHANNELS)


#BLOCK
BLOCKSIZE = 1024
num_blocks= int(math.floor(LEN/BLOCKSIZE/2))
input_tuple = [0 for n in range(0, BLOCKSIZE)]
input_tuple2 = [0 for n in range(0, BLOCKSIZE)]
output_block = [[0 for n in range(0, BLOCKSIZE)] for j in range(10)]
output_block2 = [[0 for n in range(0, BLOCKSIZE)] for j in range(10)]
output_values = [0 for n in range(0, 2*BLOCKSIZE)]


# filters
w_M = [31.25*2**n/(Fs/2) for n in range(10)]   # R = 2

b = [[0 for i in range(9)]for j in range(10)]   # 9 l * 10 h (8th-order)
a = [[0 for i in range(9)]for j in range(10)]
zi1 = [[0 for i in range(8)]for j in range(10)]
zf1 = [[0 for i in range(8)]for j in range(10)]
zi2 = [[0 for i in range(8)]for j in range(10)]
zf2 = [[0 for i in range(8)]for j in range(10)]

b[0][0:4] = [0.003153797968989,-0.012613750570327,0.018919905288632,-0.012613750570327,0.003153797968989]
a[0][0:4] = [1.000000000000000,-3.994396244687735,5.983214446700924,-3.983240096358449,0.994421894432213]
b[1][0:4] = [0.003146043882027,-0.012578425908339,0.018864765424087,-0.012578425908339,0.003146043882027]
a[1][0:4] = [1.000000000000000,-3.988772472209718,5.966420357001560,-3.966522793552386,0.988874910147887]
b[2][0:4] = [0.003127018696966,-0.012472257019470,0.018690530253927,-0.012472257019470,0.003127018696966]
a[2][0:4] = [1.000000000000000,-3.971717087369836,5.915799248577502,-3.916439310346357,0.972357203368371]
b[9][:],a[9][:] = signal.butter(4,[w_M[9]/1.414,0.99],btype='bandpass') 
zi1[9][:] = signal.lfilter_zi(b[9][:],a[9][:])
zi2[9][:] = signal.lfilter_zi(b[9][:],a[9][:])
for i in range(3,9):
    b[i][:],a[i][:] = signal.butter(4,[w_M[i]/1.414,w_M[i]*1.414],btype='bandpass') 
for i in range(0,9):    
    zi1[i][:] = signal.lfilter_zi(b[i][:],a[i][:])
    zi2[i][:] = signal.lfilter_zi(b[i][:],a[i][:])



p = pyaudio.PyAudio()
stream = p.open(format = p.get_format_from_width(WIDTH),
                channels = CHANNELS,
                rate = Fs,
                input = False,
                output = True,
                frames_per_buffer = BLOCKSIZE)
# start
print('**** Start ****')
for i in range(0,num_blocks):
    input_string = wf.readframes(BLOCKSIZE)
    input_st = struct.unpack('h' * 2 * BLOCKSIZE, input_string)
    for n in range(0,BLOCKSIZE):
        input_tuple[n]=input_st[2*n]
        input_tuple2[n]=input_st[2*n+1]

    for j in range(0,10):
        output_block[j][:],zf1[j][:] = signal.lfilter(b[j][:],a[j][:],input_tuple,zi=zi1[j][:])
        output_block2[j][:],zf2[j][:] = signal.lfilter(b[j][:],a[j][:],input_tuple2,zi=zi2[j][:])        
        zi1[j][:] = zf1[j][:]
        zi2[j][:] = zf2[j][:]
        
    for n in range(0,BLOCKSIZE):
        output_values[2*n] = clip16(Gain[0]*output_block[0][n] + Gain[1]*output_block[1][n] + Gain[2]*output_block[2][n] + Gain[3]*output_block[3][n] + Gain[4]*output_block[4][n] + Gain[5]*output_block[5][n] + Gain[6]*output_block[6][n] + Gain[7]*output_block[7][n] + Gain[8]*output_block[8][n] + Gain[9]*output_block[9][n])
        output_values[2*n+1] = clip16(Gain[0]*output_block2[0][n] + Gain[1]*output_block2[1][n] + Gain[2]*output_block2[2][n] + Gain[3]*output_block2[3][n] + Gain[4]*output_block2[4][n] + Gain[5]*output_block2[5][n] + Gain[6]*output_block2[6][n] + Gain[7]*output_block2[7][n] + Gain[8]*output_block2[8][n] + Gain[9]*output_block2[9][n])


    outputs = struct.pack('h'* 2 * BLOCKSIZE, *output_values)
    stream.write(outputs)

print('**** Done ****')
stream.stop_stream()
stream.close()
p.terminate()


