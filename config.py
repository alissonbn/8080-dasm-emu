register_descriptor = {0b000: 'B', 0b001: 'C', 0b010: 'D', 0b011: 'E', 0b100: 'H', 0b101: 'L', 0b110: 'M', 0b111: 'A'}
logic_op_descriptor = {0b000: 'ADD', 0b001: 'ADC', 0b010: 'SUB', 0b011: 'SBB', 0b100: 'ANA', 0b101: 'XRA', 0b110: 'ORA', 0b111: 'CMP'}
rotate_op_descriptor = {0b00: 'RLC', 0b01: 'RRC', 0b10: 'RAL', 0b11: 'RAR'}
register_pair_descriptor = {0b00: 'B', 0b01: 'D', 0b10: 'H', 0b11: 'PSW'}
immediate_op_descriptor = {0b00: 'SHLD', 0b01: 'LHDL', 0b10: 'STA', 0b11: 'LDA'}
jump_op_descriptor = {0b000: 'JNZ', 0b001: 'JZ', 0b010: 'JNC', 0b011: 'JC', 0b100: 'JPO', 0b101: 'JPE', 0b110: 'JP', 0b111: 'JM'}
call_op_descriptor = {0b000: 'CNZ', 0b001: 'CZ', 0b010: 'CNC', 0b011: 'CC', 0b100: 'CPO', 0b101: 'CPE', 0b110: 'CP', 0b111: 'CM'}
ret_op_descriptor = {0b000: 'RNZ', 0b001: 'RZ', 0b010: 'RNC', 0b011: 'RC', 0b100: 'RPO', 0b101: 'RPE', 0b110: 'RP', 0b111: 'RM'}
