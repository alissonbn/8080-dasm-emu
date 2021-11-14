from config import *


class CpuState:
    def __init__(self):
        # registers
        self.register = {0b000: 0, 0b001: 0, 0b010: 0, 0b011: 0, 0b100: 0, 0b101: 0, 0b110: 0, 0b111: 0}

        # memory
        self.memory = bytearray(65536)

        # program counter
        self.pc = 0

        # stack pointer
        self.sp = 0

        # condition bits
        self.carry_bit = False
        self.aux_carry_bit = False
        self.sign_bit = False
        self.zero_bit = False
        self.parity_bit = False


# adds two numbers. Returns a tuple (result, carry, auxiliary_carry_bit)
def _add(a, b):
    ha = (a & 0xF0) >> 4
    la = a & 0x0F
    hb = (b & 0xF0) >> 4
    lb = b & 0x0F
    ls = la + lb
    aux_carry = True if ls > 0xF else False
    if aux_carry:
        ha += 1
    hs = ha + hb
    res = ((hs << 4) + (ls & 0x0F))
    carry = True if res > 255 else False
    res &= 0xFFFF
    return res, carry, aux_carry


# subtracts using two's complement notation
def _sub(a, b):

    # calculate b's two complement
    b ^= 0xFFFF
    b += 1

    # now just add them
    return _add(a, b)


# I know there are much better ways to do it. I will get back to it latter (well, maybe not)
def _calculate_parity(byte):
    parity = 0
    counter = 1
    while counter < 129:
        parity += byte & counter
        counter <<= 1
    return True if parity % 2 == 0 else False


def execute_instruction(opcode, operand1, operand2, cpu_state: CpuState):
    # carry bit instructions start here
        if opcode == 0x37:
            # STC, 1 byte
            cpu_state.carry_bit = True
            return
        elif opcode == 0x3F:
            # CMC, 1 byte
            cpu_state.carry_bit = not cpu_state.carry_bit
            return
        # single register instructions start here
        elif not ((opcode & 0xC7) ^ 0x04):
            # INR, 1 byte, use the register_descriptor above on bits 2-4 to figure out operands
            register = opcode & 38

            if register == register_descriptor['M']:
                memaddr = cpu_state.register[(register_descriptor['H'] << 8) | register_descriptor['L']]
                result, carry, aux_carry = _add(cpu_state.memory[memaddr], 1)
                cpu_state.memory[memaddr] = result
                # set zero bit
                if result == 0:
                    cpu_state.zero_bit = True
                # carry flag
                cpu_state.carry_bit = carry
                cpu_state.aux_carry_bit = aux_carry
                cpu_state.parity_bit = _calculate_parity(cpu_state.memory[memaddr])
            else:
                result, carry, aux_carry = _add(cpu_state.register[register], 1)
                cpu_state.register[register] = result

                # set zero bit
                if result == 0:
                    cpu_state.zero_bit = True
                cpu_state.carry_bit = carry
                cpu_state.aux_carry_bit = aux_carry
                cpu_state.parity_bit = _calculate_parity(cpu_state.register[register])
            return

        elif not ((opcode & 0xC7) ^ 0x05):
            # DCR, 1 byte, Refer to register_descriptor above on bits 2-4 to figure out operands
            register = opcode & 38

            if register == register_descriptor['M']:
                memaddr = cpu_state.register[(register_descriptor['H'] << 8) | register_descriptor['L']]
                result, carry, aux_carry = _sub(cpu_state.memory[memaddr], 1)
                cpu_state.memory[memaddr] = result
                # set zero bit
                if result == 0:
                    cpu_state.zero_bit = True
                # carry flag
                cpu_state.carry_bit = carry
                cpu_state.aux_carry_bit = aux_carry
                cpu_state.parity_bit = _calculate_parity(cpu_state.memory[memaddr])
            else:
                result, carry, aux_carry = _sub(cpu_state.register[register], 1)
                cpu_state.register[register] = result

                # set zero bit
                if result == 0:
                    cpu_state.zero_bit = True
                cpu_state.carry_bit = carry
                cpu_state.aux_carry_bit = aux_carry
                cpu_state.parity_bit = _calculate_parity(cpu_state.register[register])
            return

        elif opcode == 0x2F:
            # CMA, 1 byte
            cpu_state.register[register_descriptor['A']] ^= 0xFFFF
            return
        elif opcode == 0x27:
            # DAA, 1 byte
            acc = cpu_state.register[register_descriptor['A']]
            acc_low = (acc & 0x00FF)
            carry = cpu_state.carry_bit
            aux_carry = cpu_state.aux_carry_bit

            if (acc_low > 9) or cpu_state.aux_carry_bit:
                acc, carry, aux_carry = _add(acc, 6)

            acc_high = (acc & 0xFF00) >> 4
            if (acc_high > 9) or carry:
                acc, carry, aux_carry = _add(acc, 6 << 4)

            cpu_state.register[register_descriptor['A']] = acc
            if acc == 0:
                cpu_state.zero_bit = True

            cpu_state.carry_bit = carry
            cpu_state.aux_carry_bit = aux_carry
            cpu_state.parity_bit = _calculate_parity(acc)
            return

        elif opcode == 0x00:
            # NOP, 1 byte
            pass
            return
        # data transfer instructions start here
        elif not ((opcode & 0xC0) ^ 0x40):
            # MOV, 1 byte, Refer to register_descriptor above on bits 2-4 to figure out operands
            dst = (opcode & 0x38) >> 3
            src = opcode & 0x07

            if dst == register_descriptor['M']:
                dst = (cpu_state.register[register_descriptor['H']] << 8) | \
                    cpu_state.register[register_descriptor['L']]
                cpu_state.memory[dst] = cpu_state.register[src]
                return

            if src == register_descriptor['M']:
                src = (cpu_state.register[register_descriptor['H']] << 8) | \
                    cpu_state.register[register_descriptor['L']]
                cpu_state.register[dst] = cpu_state.memory[src]
                return

            cpu_state.register[dst] = cpu_state.register[src]

        elif opcode == 0x02:
            # STAX B, 1 byte
            addr = (cpu_state.register[register_descriptor['B']] << 8) | cpu_state.memory[register_descriptor['C']]
            cpu_state.memory[addr] = cpu_state.register[register_descriptor['A']]

            return

        elif opcode == 0x12:
            # STAX D, 1 byte
            addr = (cpu_state.register[register_descriptor['D']] << 8) | cpu_state.memory[register_descriptor['E']]
            cpu_state.memory[addr] = cpu_state.register[register_descriptor['A']]

            return

        elif opcode == 0x0A:
            # LDAX B, 1 byte
            addr = (cpu_state.register[register_descriptor['D']] << 8) | cpu_state.memory[register_descriptor['E']]
            cpu_state.register[register_descriptor['A']] = cpu_state.memory[addr]

            return

        elif opcode == 0x1A:
            # LDAX D, 1 byte
            addr = (cpu_state.register[register_descriptor['D']] << 8) | cpu_state.memory[register_descriptor['E']]
            cpu_state.register[register_descriptor['A']] = cpu_state.memory[addr]

            return

        # register or memory to accumulator instructions start here
        elif not ((opcode & 0xC0) ^ 0x80):
            # 1 byte. refer to logic_op_descriptor and register_descriptor to figure out op and operands.
            pass
        # rotate accumulator instructions start here
        elif not ((opcode & 0xE7) ^ 0x7):
            # rotate. 1 byte refer to rotate_op_descriptor
            pass
        # register pair instructions start here
        elif not ((opcode & 0xCF) ^ 0xC5):
            # PUSH. 1 byte Refer to register_pair_descriptor
            pass
        elif not ((opcode & 0xCF) ^ 0xC1):
            # POP. t byte, refer to register_pair_descriptor
            pass
        elif not ((opcode & 0xCF) ^ 0x09):
            # DAD, 1 byte, refer to register_pair_descriptor
            pass
        elif not ((opcode & 0xCF) ^ 0x03):
            # INX, 1 byte, refer to register_pair_descriptor
            pass
        elif not ((opcode & 0xCF) ^ 0x0B):
            # DCX, 1 byte, refer to register_pair_descriptor
            pass
        elif opcode == 0xEB:
            # XCHG, 1 byte
            pass
        elif opcode == 0xE3:
            # XTHL, 1 byte
            pass
        elif opcode == 0xF9:
            # SPHL, 1 byte
            pass
        # immediate instructions start here
        elif not ((opcode & 0xCF) ^ 0x01):
            # MVI, 2 bytes, refer do register_descriptor
            pass
        elif not ((opcode & 0xC7) ^ 0x06):
            # MVI, 2 bytes, refer do register_descriptor
            pass
        elif opcode == 0xC6:
            # ADI, 2 bytes
            pass
        elif opcode == 0xCE:
            # ACI, 2 bytes
            pass
        elif opcode == 0xD6:
            # SUI, 2 bytes
            pass
        elif opcode == 0xDE:
            # SBI 2 bytes
            pass
        elif opcode == 0XE6:
            # ANI 2 bytes
            pass
        elif opcode == 0xEE:
            # XRI, 2 bytes
            pass
        elif opcode == 0xF6:
            # ORI, 2 bytes
            pass
        elif opcode == 0xFE:
            # CPI, 2 bytes
            pass
        # direct addressing instructions start here
        elif not ((opcode & 0xE7) ^ 0x22):
            # STA, LHLD, SHLD, LDA, 3 bytes, refer to immediate_op_descriptor
            pass
        # jump instructions start here. Always three bytes
        elif opcode == 0xC3:
            pass
        elif not ((opcode & 0xC6) ^ 0xC2):
            pass
        elif opcode == 0xE9:
            pass
        # call subroutine instructions start here
        elif opcode == 0xCD:
            pass
        elif not ((opcode & 0xC7) ^ 0xC4):
            pass
        # return from subroutine instructions start here
        elif opcode == 0xC9:
            pass
        elif not ((opcode & 0xC7) ^ 0xC0):
            pass
        # RST
        elif not ((opcode & 0xC7) ^ 0xC7):
            pass
        # Interrupt flip-flop instructions start here
        elif opcode == 0xFB:
            pass
        elif opcode == 0xF3:
            pass
        # Input/output instructions start here
        elif opcode == 0xDB:
            pass
        elif opcode == 0xD3:
            pass
        # HLT
        elif opcode == 0x76:
            pass
        else:
            pass
