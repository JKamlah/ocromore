class Config(object):
    DB_DIR = './Testfiles/sql/'
    NUMBER_OF_INPUTS = 3  # number of ocr inputs which will be compared, todo make this dynmically with maxlen or smth
    # keying mechanism
    DO_N_DIST_KEYING = False
    DO_MSA_BEST = True

    # Settings for N-distance keying
    NDIST_USE_WORDWISE_KEYING = False
    NDIST_MODE_ADD_LINEBREAKS = False #todo add linebreaks later!


    # Settings for Multi Sequence Alignment Best
    MSA_BEST_USE_LONGEST_PIVOT = True
    MSA_BEST_USE_N_DIST_PIVOT = True  # this is not applicable atm, it's just the longest string
    MSA_BEST_USE_CHARCONFS = True
    MSA_BEST_USE_WORDWISE_MSA = True
    MSA_BEST_USE_SEARCHSPACE = True


    # postcorrection settings:
    KEYING_RESULT_POSTCORRECTION = True

    # validation settings:
    IGNORE_LINEFEED = False
    IGNORE_WHITESPACE = False
    DISPLAY_DIFFERENCES = True
    DO_ISRI_VAL = True

    #saving file settigs
    MODE_ADD_LINEBREAKS = False  # todo add linebreaks later!

    #Filenames
    FILEPATH_MSA_BEST_RESULT = "./Testfiles/dbprof_msa_best_result.txt"
    FILEPATH_NDIST_RESULT    = "./Testfiles/dbprof_ndist_result.txt"
    FILEPATH_GROUNDTRUTH = "./Testfiles/dbprof.gt.txt"

    FILEPATH_ACCURACY_REPORT_MSA = "./Testfiles/isri_accreport_msa_best_dbprof.txt"
    FILEPATH_ACCURACY_REPORT_NDIST = "./Testfiles/isri_accreport_ndist_keying_dbprof.txt"
    FILEPATH_WACCURACY_REPORT_MSA = "./Testfiles/isri_waccreport_msa_best_dbprof.txt"
    FILEPATH_WACCURACY_REPORT_NDIST = "./Testfiles/isri_waccreport_ndist_keying_dbprof.txt"

