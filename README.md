# Register template

This is a minimum working example of rtl simulation. It uses chisel generated
verilog register with complex number input as a design-under-test.
https://github.com/Chisel-blocks/register_template

To run:
./init_submodules.sh if needed
./configure
make chisel
make sim

Simulation waits for input to finish, so hit any key to finish the simulation once done.

# Demo features

In register_template/__init__.py
Set interactive_rtl = True to see the simulation in Modelsim

Study Simulations/rtlsim/dofile.do to see how to set probes for interactive simulation

Study register_template/controller.py to learn how to build an controller 
for your rtl control signals.


