#!/usr/bin/env python

hex2bits = lambda x: ''.join([bin(b)[2:].zfill(8)[::-1] for b in x])

string2hex = lambda x: [ord(c) for c in x]

bits2hex = lambda bits: [int(bits[i:i+8][::-1],2) for i in range(0,len(bits),8)]

hexstring = lambda x: [hex(i) for i in x]


def gen_crc(data, init_state=0xaaaaaa, as_hex=True,):
  # Starting state according to BLE spec should be 0x555555
  # reverse this to so the LSB is on the left 
  state = init_state

  # Polynomial:  x^24 + x^10 + x^9 + x^6 + x^4 + x^3 + x + 1
  # 0101 1010 0110 0000 0000 0000
  lfsr_mask = 0x5a6000   

  for b_in in data:
    for i in range(8):
      next_bit = (state ^ b_in) & 1
      b_in >>=1
      state >>=1
      if(next_bit):
        state |= 1 << 23
        state ^= lfsr_mask
  if(as_hex):
    return bits2hex(bin(state)[2:].zfill(24)[::-1])
  else:
    return state

def whiten(bits, channel, as_string=True):
  # Rotate right: 0b1000001
  #           --> 0b1100000
  ror = lambda val, r_bits, max_bits: \
            ((val & (2**max_bits-1)) >> r_bits%max_bits) | \
                (val << (max_bits-(r_bits%max_bits)) & (2**max_bits-1))

  ############################################################
  # Increment 7 bit LFSR for polynomial x^7 + x^4 + 1        #
  #                                                          #
  #  x^0                       x^4              x^7     out  #
  #  ---------------------------------------------       ^   #
  #  |                          |                |       |   #
  #  --> b0 -> b1 -> b2 -> b3 - + -> b4 -> b5 -> b6 ---> +   #
  #                                                      ^   #
  #                                                      |   #
  #                                                     data #
  #                                                          #
  ############################################################
  lfsr = lambda x: (x&1)<<2 ^ ror(x,1,7)

  x = 0b1000000 | channel
  whitened = []

  for i in range(len(bits)):
    whitened.append(int(bits[i])^(x & 0b0000001))
    x = lfsr(x)

  if (as_string):
    return ''.join([str(b) for b in whitened])
  else:
    return whitened

def gen_beacon(adv_addr, message, channel, string_input=False, whitening=True):
  preamble = [0xaa]
  access_addr = [0x8e, 0x89, 0xbe, 0xd6] #bytes transmitted in reverse order
  if(string_input):
    adv_data = string2hex(message)
  else:
    adv_data = message
  pdu_len = [0x02, len(adv_addr)+len(adv_data)]
  crc = gen_crc(pdu_len + adv_addr + adv_data) 
  print("CRC")
  print(crc)
  print(''.join('{:02x}'.format(x) for x in crc))
  PDU = hex2bits(pdu_len + adv_addr + adv_data + crc)
  if(whiten):
    PDU = whiten(PDU, channel)

  return hex2bits(preamble) + hex2bits(access_addr[::-1]) + PDU

# Sample beacon receivable on phone
# Beacon name: hello
# 50 1b 03 c0 d9 7b 02 01 1a 03 03 03 18 06 09 68 65 6c 6c 6f
# Beacon name: hellooo
# 40 16 63 8a 83 66 17 4a 02 01 1a 03 03 00 18 08 09 68 65 6c 6c 6f 6f 6f
#adv_addr = [0x50, 0x1b, 0x03, 0xc0, 0xd9, 0x7b]
adv_addr = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06]
#adv_addr = [0x40, 0x16, 0x63, 0x8a, 0x83, 0x66]
beacon_name = "hellooo"
message = [0x02, 0x01, 0x1a, 0x03, 0x03, 0x03, 0x18, 0x06, 0x09] + string2hex(beacon_name)
#message = [0x17, 0x4a, 0x02, 0x01, 0x1a, 0x03, 0x03, 0x00, 0x18, 0x08, 0x09] + string2hex(beacon_name)
channel = 36

print(hex2bits([0xA7, 0x02]))
# Generate bits for a beacon packet
beacon = gen_beacon(adv_addr, message, channel)

# Print the generated bytes for debugging
print(hexstring(bits2hex(beacon)))

# Print the generated bits in a format that's easy to copy into MATLAB
print(''.join([b+' ' for b in beacon]))

count = 0;
# for b in beacon:
#   print ("\t\t8'd" + str(count) + ":\t" + "data\t=\t1'b" + b + ";");
#   count += 1;
# print("\t\tdefault:\tdata\t=\t1'b0;")

# if __name__ == "__main__":
#   print("start")
#   data = [0x01, 0x02, 0x03, 0x04]
#   crc = gen_crc(data)
#   white = whiten(hex2bits(data), 38, False)
#   print(white)

