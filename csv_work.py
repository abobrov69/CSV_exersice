from csv import *
from datetime import datetime

class BaseCSVHandler (object):
    inp_def_fldnm = ['date','customer','money']
    out_def_fldnm = ['date','customer','money']
    result = []

    def __init__ (self, fnm_in='input.csv', fnm_out='output.csv', restkey=None, restval=None, dialect="excel" ):
        self.f_in = open (fnm_in)
        self.csv_dict_reader = DictReader (self.f_in, restkey=restkey, restval=restval, dialect=dialect)
        fldnm = self.csv_dict_reader.fieldnames
        if len(fldnm) <> len (self.inp_def_fldnm):
            raise ValueError, \
                  ("incorrect number of columns in the file %f, it should have %n columns" %
                   fnm_in, len (self.inp_def_fldnm))
        else:
            chk = False
            l = ''
            for i in range (len(self.inp_def_fldnm)):
                chk = chk or fldnm[i]<>self.inp_def_fldnm[i]
                l += '"'+self.inp_def_fldnm[i]+'", '
            if chk:
                raise ValueError, \
                  ("incorrect names of columns in the file %f, they should be (%s)" %
                   fnm_in, l[:len(l)-2])
        self.f_out = open (fnm_out, 'w')
        self.csv_dict_writer = DictWriter (self.f_out, self.out_def_fldnm, dialect=dialect)

    def __iter__(self):
        return self

    def one_string_handler (self,s):
        self.result.append (s)

    def next(self):
        try:
            s = self.csv_dict_reader.next()
        except StopIteration:
            s = None
        if s:
            self.one_string_handler(s)
        return s

    def write_result (self):
        self.csv_dict_writer.writerows (self.result)

    def close_all_files (self):
        self.f_in.close ()
        self.f_out.close ()
        self.csv_dict_writer = None
        self.csv_dict_reader = None


    def process_all (self):
        for i in self.csv_dict_reader: self.next()
        self.write_result()
        self.close_all_files()

class CSVAverageCalcerMixin (object):
    out_def_fldnm = ['date','customer','average']
    wrk = {}

class CSVAvgClcWithNullAsNull (CSVAverageCalcerMixin, BaseCSVHandler)

    def __init__ (self, fnm_in='input.csv', fnm_out='output.csv', restkey=None, restval=None, dialect="excel", dateformat = '%d.%m.%Y' ):
        self.dateformat = dateformat
    return super(CSVAvgClcWithNullAsNull)

    def one_string_handler (self,s):
        csm = s['customer']
        if not csm in wrk:
            wrk[csm] = {}
        dt = datetime.strptime(s['date'])