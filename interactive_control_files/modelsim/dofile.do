add wave -position insertpoint  \
sim/:tb_register_template:io_A_0_real \
sim/:tb_register_template:io_A_0_imag \
sim/:tb_register_template:reset \
sim/:tb_register_template:initdone \
sim/:tb_register_template:clock \
sim/:tb_register_template:io_B_0_real \
sim/:tb_register_template:io_B_0_imag \

run -all

radix signal sim/:tb_register_template:io_A_0_real decimal
radix signal sim/:tb_register_template:io_A_0_imag binary
radix signal sim/:tb_register_template:io_B_0_real decimal
radix signal sim/:tb_register_template:io_B_0_imag decimal

