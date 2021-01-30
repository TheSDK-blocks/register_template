add wave -position insertpoint  \
sim/:tb_register_template:A \
sim/:tb_register_template:initdone \
sim/:tb_register_template:clock \
sim/:tb_register_template:Z \

run -all
