from csv import *
from datetime import datetime, timedelta
import decimal
from calendar import monthrange

class BaseCSVHandler (object):
    inp_def_fldnm = ['date','customer','money']
    out_def_fldnm = ['date','customer','money']
    result = []

    def __init__ (self, fnm_in='input.csv', fnm_out='output.csv', restkey=None, restval=None,
                  dialect_in="excel", dialect_out="excel" ):
        self.f_in = open (fnm_in)
        self.csv_dict_reader = DictReader (self.f_in, restkey=restkey, restval=restval, dialect=dialect_in)
        fldnm = self.csv_dict_reader.fieldnames
        if len(fldnm) <> len (self.inp_def_fldnm):
            raise ValueError, \
                  ("incorrect number of columns in the file %s, it should have %d columns" %
                   (fnm_in, len (self.inp_def_fldnm)))
        else:
            chk = False
            l = ''
            for i in range (len(self.inp_def_fldnm)):
                chk = chk or fldnm[i]<>self.inp_def_fldnm[i]
                l += '"'+self.inp_def_fldnm[i]+'", '
            if chk:
                print fnm_in, l[:len(l)-2]
                raise ValueError, \
                  ("incorrect names of columns in the file %s, they should be %s" %
                   (fnm_in,l[:len(l)-2]))
        self.f_out = open (fnm_out, 'w')
        self.csv_dict_writer = DictWriter (self.f_out, self.out_def_fldnm, dialect=dialect_out)

    def __iter__(self):
        return self

    def one_string_handler (self,s):
        if s: self.result.append (s)

    def next(self):
        return self.csv_dict_reader.next()

    def calc_result (self):
        pass

    def write_result (self):
        self.csv_dict_writer.writeheader ()
        self.csv_dict_writer.writerows (self.result)

    def close_all_files (self):
        self.f_in.close ()
        self.f_out.close ()
        self.csv_dict_writer = None
        self.csv_dict_reader = None

    def process_all (self):
        for i in self: self.one_string_handler (i)
        self.calc_result()
        self.write_result()
        self.close_all_files()

class CSVAverageCalcerMixin (object):
    out_def_fldnm = ['month','year','customer','average']
    wrk = {}

class CSVAverageCalculate (CSVAverageCalcerMixin, BaseCSVHandler):

    def __init__ (self, fnm_in='input.csv', fnm_out='output.csv', restkey=None, restval=None, dialect_in="excel",
                  dialect_out="excel", dateformat = '%d.%m.%Y', double_rec_is_error=True , spase_is_nul=True ):
        self.dateformat = dateformat
        self.double_rec_is_error = double_rec_is_error
        self.spase_is_nul = spase_is_nul
        return BaseCSVHandler.__init__ (self, fnm_in, fnm_out, restkey, restval, dialect_in, dialect_out)

    def one_string_handler (self,s):
        if not s: return
        csm = s['customer']
        if not csm in self.wrk:
            self.wrk[csm] = {}
        dt = datetime.strptime(s['date'],self.dateformat)
        mo_ye = str(dt.year)+str(dt.month).rjust(2,'0')
        if not mo_ye in self.wrk[csm]:
            self.wrk[csm][mo_ye]=[0 for i in range (monthrange(dt.year,dt.month)[1])]
        if self.wrk[csm][mo_ye][dt.day-1] == 0:
           self.wrk[csm][mo_ye][dt.day-1] = decimal.Decimal (s['money'])
        elif self.double_rec_is_error:
            raise ValueError, \
                  ("incorrect input data - double records are found, customer -  %s, date - %s" %
                   (csm, dt.strftime(self.dateformat)))
        else:
            self.wrk[csm][mo_ye][dt.day-1] += decimal.Decimal (s['money'])

    def calc_result (self):
        min_mo_ye = '9'*6
        max_mo_ye = '0'*6
        for csm in self.wrk:
            for mo_ye in self.wrk[csm]:
                min_mo_ye = min (min_mo_ye, mo_ye)
                max_mo_ye = max (max_mo_ye, mo_ye)
        dt = datetime.strptime(min_mo_ye+'01',"%Y%m%d")
        end_dt = datetime.strptime(max_mo_ye+'20',"%Y%m%d")
        while dt < end_dt:
            mo_ye = str(dt.year)+str(dt.month).rjust(2,'0')
            for csm in self.wrk:
                if mo_ye in self.wrk[csm]:
                    dct = {}
                    dct['month'] = str(dt.month).rjust(2,'0')
                    dct['year'] = str(dt.year)
                    dct['customer'] = csm
                    if self.spase_is_nul:
                        divisor = len (self.wrk[csm][mo_ye])
                    else:
                        divisor = 0
                        for i in self.wrk[csm][mo_ye]: divisor += 1 if i>0 else 0
                    dct['average'] = str( round( sum (self.wrk[csm][mo_ye]) / divisor ,2) )
                    self.result.append(dct)
            dt += timedelta(days=monthrange(dt.year,dt.month)[1])
