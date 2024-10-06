"""
=================
register_template
=================

This template is for demonstrating the elementary operations for
rtl simulations.

It utilizes Chisel generated verilog from
https://github.com/Chisel-blocks/register_template

Current docstring documentation style is Numpy
https://numpydoc.readthedocs.io/en/latest/format.html

For reference of the markup syntax
https://docutils.sourceforge.io/docs/user/rst/quickref.html

This text here is to remind you that documentation is iportant.
However, youu may find it out the even the documentation of this 
entity may be outdated and incomplete. Regardless of that, every day 
and in every way we are getting better and better :).

Initially written by Marko Kosunen, marko.kosunen@aalto.fi, 2017.


Role of section 'if __name__=="__main__"'
--------------------------------------------

This section is for self testing and interfacing of this class. The content of it is fully 
up to designer. You may use it for example to test the functionality of the class by calling it as
``python3 __init__.py``

or you may define how it handles the arguments passed during the invocation. In this example it is used 
as a complete self test script for all the simulation models defined for the register_template. 

"""

import os
import sys
if not (os.path.abspath('../../thesdk') in sys.path):
    sys.path.append(os.path.abspath('../../thesdk'))

from thesdk import *
from rtl import *
from spice import *

import numpy as np

class register_template(rtl,thesdk):
    @property
    def _classfile(self):
        return os.path.dirname(os.path.realpath(__file__)) + "/"+__name__

    def __init__(self,*arg): 
        """ register_template parameters and attributes
            Parameters
            ----------
                *arg : 
                If any arguments are defined, the first one should be the parent instance

            Attributes
            ----------
            proplist : array_like
                List of strings containing the names of attributes whose values are to be copied 
                from the parent

            Rs : float
                Sampling rate [Hz] of which the input values are assumed to change. Default: 100.0e6

            IOS : Bundle
                Members of this bundle are the IO's of the entity. See documentation of thsdk package.
                Default members defined as

                self.IOS.Members['io_A']=IO() # Pointer for input data
                self.IOS.Members['io_B']= IO() # Pointer for oputput data
                self.IOS.Members['control_write']= IO() # Pointer for control IO for rtl simulations

            model : string
                Default 'py' for Python. See documentation of thsdk package for more details.
        
            par : boolean
            Attribute to control parallel execution. How this is done is up to designer.
            Default False

            queue : array_like
            List for return values in parallel processing. This list is read by the process in parent to get the values 
            evalueted by the instance copies created during the parallel processing loop.

        """
        self.print_log(type='I', msg='Initializing %s' %(__name__)) 
        self.proplist = [ 'Rs' ];    # Properties that can be propagated from parent
        self.Rs =  100e6;            # Sampling frequency
        self.IOS.Members['io_A']=IO() # Pointer for input data
        self.IOS.Members['io_B']= IO()
        self.IOS.Members['control_write']= IO() 
        # File for control is created in controller
        self.model='py';             # Can be set externally, but is not propagated
        self.par= False              # By default, no parallel processing
        self.queue= []               # By default, no parallel processing

        # this copies the parameter values from the parent based on self.proplist
        if len(arg)>=1:
            parent=arg[0]
            self.copy_propval(parent,self.proplist)
            self.parent =parent;

        self.init()

    def init(self):
        """ Method to re-initialize the structure if the attribute values are changed after creation.

        """
        pass #Currently nohing to add

    def main(self):
        ''' The main python description of the operation. Contents fully up to designer, however, the 
        IO's should be handled bu following this guideline:
        
        To isolate the internal processing from IO connection assigments, 
        The procedure to follow is
        1) Assign input data from input to local variable
        2) Do the processing
        3) Assign local variable to output

        '''
        inval=self.IOS.Members['A'].Data
        out=np.array(1-inval)
        if self.par:
            self.queue.put(out)
        self.IOS.Members['Z'].Data=out

    def run(self,*arg):
        ''' The default name of the method to be executed. This means: parameters and attributes 
            control what is executed if run method is executed. By this we aim to avoid the need of 
            documenting what is the execution method. It is always self.run. 

            Parameters
            ----------
            *arg :
                The first argument is assumed to be the queue for the parallel processing defined in the parent, 
                and it is assigned to self.queue and self.par is set to True. 
        
        '''
        if len(arg)>0:
            self.par=True      #flag for parallel processing
            self.queue=arg[0]  #multiprocessing.queue as the first argument

        if self.model=='py':
            #self.main()
            self.print_log(type='F', msg='Python model currently not supported')
        elif self.model in [ 'sv', 'icarus', 'verilator' ]:
              # Verilog simulation options here
              inputnames=[]
              outputnames=[]
              for i in range(8):
                  inputnames.extend(['io_A_%s_real' %(i), 'io_A_%s_imag' %(i)])
                  outputnames.extend(['io_B_%s_real' %(i), 'io_B_%s_imag' %(i)])
              f1=rtl_iofile(self, name='io_A', dir='in', iotype='sample',
                      ionames=inputnames, datatype='scomplex') # IO file for input A
              f2=rtl_iofile(self, name='io_B', dir='out', iotype='sample',
                      ionames=outputnames, datatype='scomplex')
              if self.lang == 'sv':
                    f1.rtl_io_sync='@(negedge clock)'
                    f2.rtl_io_sync='@(negedge clock)'
              elif self.lang == 'vhdl':
                    f1.rtl_io_sync='falling_edge(clock)'
                    f2.rtl_io_sync='falling_edge(clock)'
              self.rtlparameters=dict([ ('g_Rs',('real', self.Rs) )]) #Defines the sample rate
              self.run_rtl()
        else:
            self.print_log(type='F', msg='Requested model currently not supported')

    def define_io_conditions(self):
        '''This overloads the method called by run_rtl method. It defines the read/write conditions for the files

        '''
        if self.lang == 'vhdl':
            # Input A is read to verilog simulation after 'initdone' is set to 1 by controller
            self.iofile_bundle.Members['io_A'].rtl_io_condition='(initdone=\'1\')'
            # Output is read to verilog simulation when all of the outputs are valid, 
            # and after 'initdone' is set to 1 by controller
            self.iofile_bundle.Members['io_B'].rtl_io_condition_append(cond='and (initdone=\'1\')')
        if self.lang == 'sv':
            # Input A is read to verilog simulation after 'initdone' is set to 1 by controller
            self.iofile_bundle.Members['io_A'].rtl_io_condition='initdone'
            # Output is read to verilog simulation when all of the outputs are valid, 
            # and after 'initdone' is set to 1 by controller
            self.iofile_bundle.Members['io_B'].rtl_io_condition_append(cond='&& initdone')


if __name__=="__main__":
    import matplotlib.pyplot as plt
    from  register_template import *
    from  register_template.controller import controller as register_template_controller
    import pdb
    length=1024
    rs=100e6 
    # Gives random numbers over 16 range. These are interpreted as signed
    indata=(np.random.randint(-2**15-1, high=2**15,size=length).reshape(-1,1)
        +1j*np.random.randint(-2**15-1, high=2**15,size=length).reshape(-1,1)); 
    indata=indata.reshape((128,8))
    controller=register_template_controller()
    controller.Rs=rs
    controller.reset()
    controller.step_time()
    controller.start_datafeed()
    models=[ 'icarus', 'verilator' ]
    # Enables VHDL testbench
    #lang='vhdl'
    lang='sv'
    duts=[]
    for model in models:
        d=register_template()
        duts.append(d) 
        d.model=model
        d.lang=lang
        d.Rs=rs
        # For debugging
        #d.preserve_iofiles= True
        #d.preserve_rtlfiles= True
        # To see in Modelsim, what happens in the simulation
        # See Simulations/rtlsim/dofile.do for control
        #d.interactive_rtl=True
        d.IOS.Members['io_A'].Data=indata.reshape((128,8))
        # Datafield of control_write IO is a type iofile, 
        # Method rtl.create_connectors adopts it to be iofile of dut.  
        d.IOS.Members['control_write']=controller.IOS.Members['control_write']
        d.init()
        d.run()
    # Obs the latencies may be different
    latency=[ 0 , 0, 0, 0 ]
    for k in range(len(duts)):
        hfont = {'fontname':'Sans'}
        figure,axes=plt.subplots(2,1,sharex=True)
        #x = np.linspace(0,10,11).reshape(-1,1)
        axes[0].plot(duts[k].IOS.Members['io_A'].Data[:,0].real)
        axes[0].set_ylim(-2**15, 1.1*2**15);
        axes[0].set_xlim((0,indata.shape[0]));
        axes[0].set_ylabel('Input', **hfont,fontsize=18);
        axes[0].grid(True)
        axes[1].plot(duts[k].IOS.Members['io_B'].Data[:,0].real)
        axes[1].set_ylim(-2**15, 1.1*2**15);
        axes[0].set_xlim((0,duts[k].IOS.Members['io_A'].Data.real.shape[0]));
        axes[1].set_ylabel('Output', **hfont,fontsize=18);
        axes[1].set_xlabel('Sample (n)', **hfont,fontsize=18);
        axes[1].grid(True)
        titlestr = "register_template model %s" %(duts[k].model) 
        plt.suptitle(titlestr,fontsize=20);
        plt.grid(True);
        printstr="./inv_%s.eps" %(duts[k].model)
        plt.show(block=False);
        figure.savefig(printstr, format='eps', dpi=300);
    # Remove this if you do not want to see the images
    input()
