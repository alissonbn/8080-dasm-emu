from config import *

def write_output(output, outfile, breakLine = True):
    if(breakLine):
        outfile.writelines(output + '\n')
    else:
        outfile.write(output)

def dasm(filename, offset = 0):
    output = open('../output.asm', 'w')
    rom = open(filename, 'rb')
    image = rom.read()
    i = offset
    while i < len(image):
        opcode = image[i]
        write_output('{0:0>5X}:{1:0>2X}\t'.format(i, opcode), output, False)
        #carry bit instrutions start here
        if opcode == 0x37:
            #STC, 1 byte
            write_output('STC', output)
            i += 1
        elif opcode == 0x3F:
            #CMC, 1 byte
            write_output('CMC', output)
            i += 1
        #single register instructions start here
        elif not ((opcode & 0xC7) ^ 0x04):
            #INR, 1 byte, use the register_descriptor above on bits 2-4 to figure out operands
            write_output('INR ' + register_descriptor[(opcode & 0b00011100) >> 2], output)
            i += 1
        elif not ((opcode & 0xC7) ^  0x05):
            #DCR, 1 byte, Refer to register_descriptor above on bits 2-4 to figure out operands
            write_output('DCR ' + register_descriptor[(opcode & 0b00011100) >> 2], output)
            i += 1
        elif opcode == 0x2F:
            #CMA, 1 byte
            write_output('CMA', output)
            i += 1
        elif opcode == 0x27:
            #DAA, 1 byte
            write_output('DAA', output)
            i += 1
        elif opcode == 0x00:
            #NOP, 1 byte
            write_output('NOP', output)
            i += 1
        #data transfer instructions start here
        elif not ((opcode & 0xC0) ^ 0x40):
            #MOV, 1 byte, Refer to register_descriptor above on bits 2-4 to figure out operands
            write_output('MOV ' + register_descriptor[(opcode & 0b00111000) >> 3] + ', ' + register_descriptor[opcode & 0b00000111], output)
            i += 1
        elif opcode == 0x02:
            #STAX B, 1 byte
            write_output('STAX B', output)
            i += 1
        elif opcode == 0x12:
            #STAX D, 1 byte
            write_output('STAX D', output)
            i += 1
        elif opcode == 0x0A:
            #LDAX B, 1 byte
            write_output('LDAX B', output)
            i += 1
        elif opcode == 0x1A:
            #LDAX D, 1 byte
            write_output('LDAX D', output)
            i += 1
        #register or memory to accumulator instructions start here
        elif not ((opcode & 0xC0) ^ 0x80):
            #1 byte. refer to logic_op_descriptor and register_descriptor to figure out op and operands.
            write_output(logic_op_descriptor[(opcode & 0b00111000) >> 3] + ' ' + register_descriptor[(opcode & 0b00000111)], output)
            i += 1
        #rotate accumulator instructions start here
        elif not ((opcode & 0xE7) ^ 0x7):
            #rotate. 1 byte refer to rotate_op_descriptor
            write_output(rotate_op_descriptor[(opcode & 0b00011000) > 3], output)
            i += 1
        #register pair instructions start here
        elif not ((opcode & 0xCF) ^ 0xC5):
            #PUSH. 1 byte Refer to register_pair_descriptor
            write_output('PUSH ' + register_pair_descriptor[(opcode & 0b00110000) >> 4], output)
            i += 1
        elif not ((opcode & 0xCF) ^ 0xC1):
            #POP. t byte, refer to register_pair_descriptor
            write_output('POP ' + register_pair_descriptor[(opcode & 0b00110000) >> 4], output)
            i += 1
        elif not ((opcode & 0xCF) ^  0x09):
            #DAD, 1 byte, refer to register_pair_descriptor
            write_output('DAD ' + register_pair_descriptor[(opcode & 0b00110000) >> 4], output)
            i += 1
        elif not ((opcode & 0xCF) ^ 0x03):
            #INX, 1 byte, refer to register_pair_descriptor
            write_output('INX ' + register_pair_descriptor[(opcode & 0b00110000) >> 4], output)
            i += 1
        elif not ((opcode & 0xCF) ^ 0x0B):
            #DCX, 1 byte, refer to register_pair_descriptor
            write_output('DCX ' + register_pair_descriptor[(opcode & 0b00110000) >> 4], output)
            i += 1
        elif opcode == 0xEB:
            #XCHG, 1 byte
            write_output('XCHG', output)
            i += 1
        elif opcode == 0xE3:
            #XTHL, 1 byte
            write_output('XTHL', output)
            i += 1
        elif opcode == 0xF9:
            #SPHL, 1 byte
            write_output('SPHL', output)
            i += 1
        #immediate instructions start here
        elif not ((opcode & 0xCF) ^ 0x01):
            #MVI, 2 bytes, refer do register_descriptor
            write_output('LXI {0}, {1:0>5X}H'.format(register_pair_descriptor[(opcode & 0b00110000) >> 4], image[i+1], (image[i + 1] + image[i + 2] << 8)), output)
            i += 3
        elif not ((opcode & 0xC7) ^ 0x06):
            #MVI, 2 bytes, refer do register_descriptor
            write_output('MVI {0}, {1:0>2X}H'.format(register_descriptor[(opcode & 0b00111000) >> 3], image[i+1]), output)
            i += 2
        elif opcode == 0xC6:
            #ADI, 2 bytes
            write_output('ADI {0:0>2X}H'.format(image[i+1]), output)
            i += 2
        elif opcode == 0xCE:
            #ACI, 2 bytes
            write_output('ACI {0:0>2X}H'.format(image[i+1]), output)
            i += 2
        elif opcode == 0xD6:
            #SUI, 2 bytes
            write_output('SUI {0:0>2X}H'.format(image[i+1]), output)
            i += 2
        elif opcode == 0xDE:
            #SBI 2 bytes
            write_output('SBI {0:0>2X}H'.format(image[i+1]), output)
            i += 2
        elif opcode == 0XE6:
            #ANI 2 bytes
            write_output('ANI {0:0>2X}H'.format(image[i+1]), output)
            i += 2
        elif opcode == 0xEE:
            #XRI, 2 bytes
            write_output('XRI {0:0>2X}H'.format(image[i+1]), output)
            i += 2
        elif opcode == 0xF6:
            #ORI, 2 bytes
            write_output('ORI {0:0>2X}H'.format(image[i+1]), output)
            i += 2
        elif opcode == 0xFE:
            #CPI, 2 bytes
            write_output('CPI {0:0>2X}H'.format(image[i+1]), output)
            i += 2
        #direct addressing instructions start here
        elif not ((opcode & 0xE7) ^ 0x22):
            #STA, LHLD, SHLD, LDA, 3 bytes, refer to immediate_op_descriptor
            write_output('{0} {1:0>5X}H'.format(immediate_op_descriptor[opcode & 0b00011000 >> 3], (image[i + 1] + image[i + 2] << 8)), output)
            i += 3
        #jump instructions start here. Always three bytes
        elif opcode == 0xC3:
            write_output('JMP {0:0>5X}H'.format(image[i + 1] + (image[i + 2] << 8)), output)
            i += 3
        elif not ((opcode & 0xC6) ^ 0xC2):
            write_output('{0} {1:0>5X}H'.format(jump_op_descriptor[opcode & 0b00111000 >> 3], (image[i + 1] + image[i + 2] << 8)), output)
            i += 3
        elif opcode == 0xE9:
            write_output('PCHL', output)
            i += 1
        #call subroutine instructions start here
        elif opcode == 0xCD:
            write_output('CALL {0:0>5X}H'.format(image[i + 1] + (image[i + 2] << 8)), output)
            i += 3
        elif not ((opcode & 0xC7) ^ 0xC4):
            write_output('{0} {1:0>5X}H'.format(call_op_descriptor[opcode & 0b00111000 >> 3], (image[i + 1] + image[i + 2] << 8)), output)
            i += 3
        #return from subroutine instructions start here
        elif opcode == 0xC9:
            write_output('RET', output)
            i += 1
        elif not ((opcode & 0xC7) ^ 0xC0):
            write_output(ret_op_descriptor[0b00111000 >> 3], output)
            i += 1
        #RST
        elif not ((opcode & 0xC7) ^ 0xC7):
            write_output('RST {0:0>2X}H'.format(opcode & 0b00111000 >> 3), output)
            i += 1
        #Interrupt flip-flop instructions start here
        elif opcode == 0xFB:
            write_output('EI', output)
            i += 1
        elif opcode == 0xF3:
            write_output('DI', output)
            i += 1
        #Input/output instrutctions start here
        elif opcode == 0xDB:
            write_output('IN {0:0>2X}H'.format(image[i+1]), output)
            i += 2
        elif opcode == 0xD3:
            write_output('OUT {0:0>2X}H'.format(image[i+1]), output)
            i += 2
        #HLT
        elif opcode == 0x76:
            write_output('HLT', output)
            i += 2
        else:
            write_output('NE', output)
            i += 1
    output.close()
    rom.close()


if __name__ == '__main__':
    import sys
    defaultRom = '../invaders.rom'
    defaultOffset = '-o 0x50'
    #if(len(sys.argv) < 2):
    #    raise(Exception('dasm.py input [-o hexOffset]'))
    offset = 0
    printToScreen = False
    #below is something very very ugly in order to run this from idle
    sys.argv.append(defaultRom)
    sys.argv.append(defaultOffset)
    #above is something very very ugly in order to run this from idle
    filename = sys.argv[1]
    for i in sys.argv[2:]:
        if i.startswith('-o'):
            offset = int(i[3:], 16)
        else:
            raise Exception('Invalid arguments')         
    dasm(filename, offset)
