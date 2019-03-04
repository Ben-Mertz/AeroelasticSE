import os
import subprocess

class FastWrapper(object):

    def __init__(self, **kwargs):
        self.FAST_ver = 'OPENFAST' #(FAST7, FAST8, OPENFAST)

        self.FAST_exe = None   # Path to executable
        self.FAST_InputFile = None   # FAST input file (ext=.fst)
        self.FAST_directory = None   # Path to fst directory files
        self.debug_level = 0 #(0:quiet, 1:output task description, 2:full FAST stdout)

        # Optional population class attributes from key word arguments
        for k, w in kwargs.iteritems():
            try:
                setattr(self, k, w)
            except:
                pass

        super(FastWrapper, self).__init__()

    def execute(self):

        self.input_file = os.path.join(self.FAST_directory, self.FAST_InputFile)

        exec_str = []
        exec_str.append(self.FAST_exe)
        exec_str.append(self.FAST_InputFile)

        olddir = os.getcwd()
        os.chdir(self.FAST_directory)

        if self.debug_level > 0:
            print "EXECUTING", self.FAST_ver
            print "Executable: \t", self.FAST_exe 
            print "Run directory: \t", self.FAST_directory
            print "Input file: \t", self.FAST_InputFile
            print "Exec string: \t", exec_str

        if self.debug_level > 1:
            subprocess.call(exec_str)
        else:
            FNULL = open(os.devnull, 'w')
            subprocess.call(exec_str, stdout=FNULL, stderr=subprocess.STDOUT)
        
        os.chdir(olddir)

if __name__=="__main__":


    fast = FastWrapper(debug_level=2)

    fast.FAST_ver = 'FAST8'

    if fast.FAST_ver == 'FAST7':
        fast.FAST_exe = 'C:/Users/egaertne/WT_Codes/FAST_v7.02.00d-bjj/FAST.exe'   # Path to executable
        fast.FAST_InputFile = 'test.fst'   # FAST input file (ext=.fst)
        fast.FAST_directory = 'C:/Users/egaertne/WISDEM/AeroelasticSE/src/AeroelasticSE/FAST_mdao/temp/FAST7'   # Path to fst directory files

    elif fast.FAST_ver == 'FAST8':
        fast.FAST_exe = 'C:/Users/egaertne/WT_Codes/FAST_v8.16.00a-bjj/bin/FAST_Win32.exe'   # Path to executable
        fast.FAST_InputFile = 'test.fst'   # FAST input file (ext=.fst)
        fast.FAST_directory = 'C:/Users/egaertne/WISDEM/AeroelasticSE/src/AeroelasticSE/FAST_mdao/temp/FAST8'   # Path to fst directory files

    elif fast.FAST_ver == 'OPENFAST':
        fast.FAST_exe = 'C:/Users/egaertne/WT_Codes/openfast/build/glue-codes/fast/openfast.exe'   # Path to executable
        fast.FAST_InputFile = 'test.fst'   # FAST input file (ext=.fst)
        fast.FAST_directory = 'C:/Users/egaertne/WISDEM/AeroelasticSE/src/AeroelasticSE/FAST_mdao/temp/OpenFAST'   # Path to fst directory files

    fast.execute()