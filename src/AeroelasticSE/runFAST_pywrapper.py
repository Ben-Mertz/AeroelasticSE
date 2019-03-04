"""
A basic python script that demonstrates how to use the FST8 reader, writer, and wrapper in a purely
python setting. These functions are constructed to provide a simple interface for controlling FAST
programmatically with minimal additional dependencies.
"""
# Hacky way of doing relative imports
import os, sys, time
import multiprocessing as mp
# sys.path.insert(0, os.path.abspath(".."))

from FAST_reader import InputReader_Common, InputReader_OpenFAST, InputReader_FAST7
from FAST_writer import InputWriter_Common, InputWriter_OpenFAST, InputWriter_FAST7
from FAST_wrapper import FastWrapper

class runFAST_pywrapper(object):

    def __init__(self, **kwargs):
        self.FAST_ver = 'OPENFAST' #(FAST7, FAST8, OPENFAST)

        self.FAST_exe = None
        self.FAST_InputFile = None
        self.FAST_directory = None
        self.FAST_runDirectory = None
        self.FAST_namingOut = None
        self.read_yaml = False
        self.write_yaml = False
        self.fst_vt = {}
        self.case = {}                  # dictionary of variable values to change
        self.channels = {}              # dictionary of output channels to change
        self.debug_level   = 0
        self.dev_branch = False

        # Optional population class attributes from key word arguments
        for k, w in kwargs.iteritems():
            try:
                setattr(self, k, w)
            except:
                pass

        super(runFAST_pywrapper, self).__init__()

    def execute(self):
        # FAST version specific initialization
        if self.FAST_ver.lower() == 'fast7':
            reader = InputReader_FAST7(FAST_ver=self.FAST_ver)
            writer = InputWriter_FAST7(FAST_ver=self.FAST_ver)
        elif self.FAST_ver.lower() in ['fast8','openfast']:
            reader = InputReader_OpenFAST(FAST_ver=self.FAST_ver)
            writer = InputWriter_OpenFAST(FAST_ver=self.FAST_ver)
        wrapper = FastWrapper(FAST_ver=self.FAST_ver, debug_level=self.debug_level)

        # Read input model, FAST files or Yaml
        if self.fst_vt == {}:
            if self.read_yaml:
                reader.FAST_yamlfile = self.FAST_yamlfile_in
                reader.read_yaml()
            else:
                reader.FAST_InputFile = self.FAST_InputFile
                reader.FAST_directory = self.FAST_directory
                reader.dev_branch = self.dev_branch
                reader.execute()
        
            # Initialize writer variables with input model
            writer.fst_vt = reader.fst_vt
        else:
            writer.fst_vt = self.fst_vt
        writer.FAST_runDirectory = self.FAST_runDirectory
        writer.FAST_namingOut = self.FAST_namingOut
        writer.dev_branch = self.dev_branch
        # Make any case specific variable changes
        if self.case:
            writer.update(fst_update=self.case)
        # Modify any specified output channels
        if self.channels:
            writer.update_outlist(self.channels)
        # Write out FAST model
        writer.execute()
        if self.write_yaml:
            writer.FAST_yamlfile = self.FAST_yamlfile_out
            writer.write_yaml()

        # Run FAST
        wrapper.FAST_exe = self.FAST_exe
        wrapper.FAST_InputFile = os.path.split(writer.FAST_InputFileOut)[1]
        wrapper.FAST_directory = os.path.split(writer.FAST_InputFileOut)[0]
        wrapper.execute()

        FAST_Output = os.path.join(wrapper.FAST_directory, wrapper.FAST_InputFile[:-3]+'outb')
        return FAST_Output

class runFAST_pywrapper_batch(object):

    def __init__(self, **kwargs):

        self.FAST_ver           = 'OpenFAST'
        self.FAST_exe           = None
        self.FAST_InputFile     = None
        self.FAST_directory     = None
        self.FAST_runDirectory  = None
        self.debug_level        = 0
        self.dev_branch         = False

        self.read_yaml          = False
        self.FAST_yamlfile_in   = ''
        self.fst_vt             = {}
        self.write_yaml         = False
        self.FAST_yamlfile_out  = ''

        self.case_list          = []
        self.case_name_list     = []
        self.channels           = {}

        self.post               = None

        # Optional population of class attributes from key word arguments
        for k, w in kwargs.iteritems():
            try:
                setattr(self, k, w)
            except:
                pass

        super(runFAST_pywrapper_batch, self).__init__()

        
    def run_serial(self):
        # Run batch serially

        if not os.path.exists(self.FAST_runDirectory):
            os.makedirs(self.FAST_runDirectory)

        out = [None]*len(self.case_list)
        for i, (case, case_name) in enumerate(zip(self.case_list, self.case_name_list)):
            out[i] = eval(case, case_name, self.FAST_ver, self.FAST_exe, self.FAST_runDirectory, self.FAST_InputFile, self.FAST_directory, self.read_yaml, self.FAST_yamlfile_in, self.fst_vt, self.write_yaml, self.FAST_yamlfile_out, self.channels, self.debug_level, self.dev_branch, self.post)

        return out

    def run_multi(self, cores=None):
        # Run cases in parallel, threaded with multiprocessing module

        if not os.path.exists(self.FAST_runDirectory):
            os.makedirs(self.FAST_runDirectory)

        if not cores:
            cores = mp.cpu_count()
        pool = mp.Pool(cores)

        case_data_all = []
        for i in range(len(self.case_list)):
            case_data = []
            case_data.append(self.case_list[i])
            case_data.append(self.case_name_list[i])
            case_data.append(self.FAST_ver)
            case_data.append(self.FAST_exe)
            case_data.append(self.FAST_runDirectory)
            case_data.append(self.FAST_InputFile)
            case_data.append(self.FAST_directory)
            case_data.append(self.read_yaml)
            case_data.append(self.FAST_yamlfile_in)
            case_data.append(self.fst_vt)
            case_data.append(self.write_yaml)
            case_data.append(self.FAST_yamlfile_out)
            case_data.append(self.channels)
            case_data.append(self.debug_level)
            case_data.append(self.dev_branch)
            case_data.append(self.post)

            case_data_all.append(case_data)

        return pool.map(eval_multi, case_data_all)

    def run_mpi(self):
        # Run in parallel with mpi, not yet implimented
        print 'MPI interfaced not yet implimented'


def eval(case, case_name, FAST_ver, FAST_exe, FAST_runDirectory, FAST_InputFile, FAST_directory, read_yaml, FAST_yamlfile_in, fst_vt, write_yaml, FAST_yamlfile_out, channels, debug_level, dev_branch, post):
    # Batch FAST pyWrapper call, as a function outside the runFAST_pywrapper_batch class for pickle-ablility

    fast = runFAST_pywrapper(FAST_ver=FAST_ver)
    fast.FAST_exe           = FAST_exe
    fast.FAST_InputFile     = FAST_InputFile
    fast.FAST_directory     = FAST_directory
    fast.FAST_runDirectory  = FAST_runDirectory
    fast.dev_branch         = dev_branch

    fast.read_yaml          = read_yaml
    fast.FAST_yamlfile_in   = FAST_yamlfile_in
    fast.fst_vt             = fst_vt
    fast.write_yaml         = write_yaml
    fast.FAST_yamlfile_out  = FAST_yamlfile_out

    fast.FAST_namingOut     = case_name
    fast.case               = case
    fast.channels           = channels
    fast.debug_level        = debug_level

    FAST_Output = fast.execute()

    # Post process
    if post:
        out = post(FAST_Output)
    else:
        out = []

    return out

def eval_multi(data):
    # helper function for running with multiprocessing.Pool.map
    # converts list of arguement values to arguments
    return eval(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11], data[12], data[13], data[14], data[15])

def example_runFAST_pywrapper_batch():
    """ 
    Example of running a batch of cases, in serial or in parallel
    """

    fastBatch = runFAST_pywrapper_batch(FAST_ver='OpenFAST')

    fastBatch.FAST_exe = 'C:/Users/egaertne/WT_Codes/openfast/build/glue-codes/fast/openfast.exe'   # Path to executable
    fastBatch.FAST_InputFile = '5MW_Land_DLL_WTurb.fst'   # FAST input file (ext=.fst)
    fastBatch.FAST_directory = 'C:/Users/egaertne/WT_Codes/models/openfast/glue-codes/fast/5MW_Land_DLL_WTurb'   # Path to fst directory files
    fastBatch.FAST_runDirectory = 'temp/OpenFAST'
    fastBatch.debug_level = 2

    ## Define case list explicitly
    # case_list = [{}, {}]
    # case_list[0]['Fst', 'TMax'] = 4.
    # case_list[1]['Fst', 'TMax'] = 5.
    # case_name_list = ['test01', 'test02']

    ## Generate case list using General Case Generator
    ## Specify several variables that change independently or collectly
    case_inputs = {}
    case_inputs[("Fst","TMax")] = {'vals':[10.], 'group':0}
    case_inputs[("InflowWind","WindType")] = {'vals':[1], 'group':0}
    case_inputs[("Fst","OutFileFmt")] = {'vals':[2], 'group':0}
    case_inputs[("InflowWind","HWindSpeed")] = {'vals':[8., 9., 10., 11., 12.], 'group':1}
    case_inputs[("ElastoDyn","RotSpeed")] = {'vals':[9.156, 10.296, 11.431, 11.89, 12.1], 'group':1}
    case_inputs[("ElastoDyn","BlPitch1")] = {'vals':[0., 0., 0., 0., 3.823], 'group':1}
    case_inputs[("ElastoDyn","BlPitch2")] = case_inputs[("ElastoDyn","BlPitch1")]
    case_inputs[("ElastoDyn","BlPitch3")] = case_inputs[("ElastoDyn","BlPitch1")]
    case_inputs[("ElastoDyn","GenDOF")] = {'vals':['True','False'], 'group':2}
    
    from CaseGen_General import CaseGen_General
    case_list, case_name_list = CaseGen_General(case_inputs, dir_matrix=fastBatch.FAST_runDirectory, namebase='testing')

    fastBatch.case_list = case_list
    fastBatch.case_name_list = case_name_list

    # fastBatch.run_serial()
    fastBatch.run_multi(2)


def example_runFAST_CaseGenIEC():

    from CaseGen_IEC import CaseGen_IEC
    iec = CaseGen_IEC()

    # Turbine Data
    iec.init_cond = {} # can leave as {} if data not available
    iec.init_cond[("ElastoDyn","RotSpeed")] = {'U':[3., 4., 5., 6., 7., 8., 9., 10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24., 25]}
    iec.init_cond[("ElastoDyn","RotSpeed")]['val'] = [6.972, 7.183, 7.506, 7.942, 8.469, 9.156, 10.296, 11.431, 11.89, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1]
    iec.init_cond[("ElastoDyn","BlPitch1")] = {'U':[3., 4., 5., 6., 7., 8., 9., 10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24., 25]}
    iec.init_cond[("ElastoDyn","BlPitch1")]['val'] = [0., 0., 0., 0., 0., 0., 0., 0., 0., 3.823, 6.602, 8.668, 10.450, 12.055, 13.536, 14.920, 16.226, 17.473, 18.699, 19.941, 21.177, 22.347, 23.469]
    iec.init_cond[("ElastoDyn","BlPitch2")] = iec.init_cond[("ElastoDyn","BlPitch1")]
    iec.init_cond[("ElastoDyn","BlPitch3")] = iec.init_cond[("ElastoDyn","BlPitch1")]

    iec.Turbine_Class = 'I' # I, II, III, IV
    iec.Turbulence_Class = 'A'
    iec.D = 126.
    iec.z_hub = 90.

    # DLC inputs
    iec.dlc_inputs = {}
    iec.dlc_inputs['DLC']   = [1.1, 1.5]
    iec.dlc_inputs['U']     = [[8, 9, 10], [12]]
    iec.dlc_inputs['Seeds'] = [[5, 6, 7], []]
    iec.dlc_inputs['Yaw']   = [[], []]

    iec.transient_dir_change        = 'both'  # '+','-','both': sign for transient events in EDC, EWS
    iec.transient_shear_orientation = 'both'  # 'v','h','both': vertical or horizontal shear for EWS

    # Naming, file management, etc
    iec.wind_dir = 'temp/wind'
    iec.case_name_base = 'testing'
    iec.Turbsim_exe = 'C:/Users/egaertne/WT_Codes/Turbsim_v2.00.07/bin/TurbSim_x64.exe'
    iec.debug_level = 2
    iec.parallel_windfile_gen = True
    iec.cores = 4
    iec.run_dir = 'temp/OpenFAST'

    # Run case generator / wind file writing
    case_inputs = {}
    case_inputs[('Fst','OutFileFmt')] = {'vals':[1], 'group':0}
    case_list, case_name_list = iec.execute(case_inputs=case_inputs)

    # Run FAST cases
    fastBatch = runFAST_pywrapper_batch(FAST_ver='OpenFAST')
    fastBatch.FAST_exe = 'C:/Users/egaertne/WT_Codes/openfast/build/glue-codes/fast/openfast.exe'   # Path to executable
    fastBatch.FAST_InputFile = '5MW_Land_DLL_WTurb.fst'   # FAST input file (ext=.fst)
    fastBatch.FAST_directory = 'C:/Users/egaertne/WT_Codes/models/openfast/glue-codes/fast/5MW_Land_DLL_WTurb'   # Path to fst directory files
    fastBatch.FAST_runDirectory = iec.run_dir

    fastBatch.case_list = case_list
    fastBatch.case_name_list = case_name_list
    fastBatch.debug_level = 2

    # fastBatch.run_serial()
    fastBatch.run_multi(4)

    
def example_runFAST_pywrapper():
    """ 
    Example of reading, writing, and running FAST 7, 8 and OpenFAST.
    """

    FAST_ver = 'OpenFAST'
    dev_branch = True
    fast = runFAST_pywrapper(FAST_ver=FAST_ver, dev_branch=dev_branch)

    if FAST_ver.lower() == 'fast7':
        fast.FAST_exe = 'C:/Users/egaertne/WT_Codes/FAST_v7.02.00d-bjj/FAST.exe'   # Path to executable
        fast.FAST_InputFile = 'Test12.fst'   # FAST input file (ext=.fst)
        fast.FAST_directory = 'C:/Users/egaertne/WT_Codes/models/FAST_v7.02.00d-bjj/CertTest/'   # Path to fst directory files
        fast.FAST_runDirectory = 'temp/FAST7'
        fast.FAST_namingOut = 'test'

    elif FAST_ver.lower() == 'fast8':
        fast.FAST_exe = 'C:/Users/egaertne/WT_Codes/FAST_v8.16.00a-bjj/bin/FAST_Win32.exe'   # Path to executable
        fast.FAST_InputFile = 'NREL5MW_onshore.fst'   # FAST input file (ext=.fst)
        fast.FAST_directory = 'C:/Users/egaertne/WT_Codes/models/FAST_v8.16.00a-bjj/ref/5mw_onshore/'   # Path to fst directory files
        fast.FAST_runDirectory = 'temp/FAST8'
        fast.FAST_namingOut = 'test'

    # elif FAST_ver.lower() == 'openfast':
    #     fast.FAST_exe = 'C:/Users/egaertne/WT_Codes/openfast/build/glue-codes/fast/openfast.exe'   # Path to executable
    #     fast.FAST_InputFile = '5MW_Land_DLL_WTurb.fst'   # FAST input file (ext=.fst)
    #     fast.FAST_directory = 'C:/Users/egaertne/WT_Codes/models/openfast/glue-codes/fast/5MW_Land_DLL_WTurb'   # Path to fst directory files
    #     fast.FAST_runDirectory = 'temp/OpenFAST'
    #     fast.FAST_namingOut = 'test'

    #     fast.read_yaml = False
    #     fast.FAST_yamlfile_in = 'temp/OpenFAST/test.yaml'

    #     fast.write_yaml = False
    #     fast.FAST_yamlfile_out = 'temp/OpenFAST/test.yaml'
    elif FAST_ver.lower() == 'openfast':
        fast.FAST_exe = 'C:/Users/egaertne/WT_Codes/openfast-dev/build/glue-codes/openfast/openfast.exe'   # Path to executable
        fast.FAST_InputFile = '5MW_Land_DLL_WTurb.fst'   # FAST input file (ext=.fst)
        fast.FAST_directory = 'C:/Users/egaertne/WT_Codes/models/openfast-dev/r-test/glue-codes/openfast/5MW_Land_DLL_WTurb'   # Path to fst directory files
        fast.FAST_runDirectory = 'temp/OpenFAST'
        fast.FAST_namingOut = 'test'

        fast.read_yaml = False
        fast.FAST_yamlfile_in = 'temp/OpenFAST/test.yaml'

        fast.write_yaml = False
        fast.FAST_yamlfile_out = 'temp/OpenFAST/test.yaml'

    fast.execute()


if __name__=="__main__":

    example_runFAST_pywrapper()
    # example_runFAST_pywrapper_batch()
    # example_runFAST_CaseGenIEC()