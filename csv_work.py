from csv import *
from datetime import datetime, timedelta
import decimal
from calendar import monthrange

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
        print s
        self.result.append (s)

    def next(self):
        try:
            s = self.csv_dict_reader.next()
        except StopIteration:
            s = None
#        print 'nxt',s
#        if s:
#            self.one_string_handler(s)
        return s

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
        for i in self.csv_dict_reader: self.one_string_handler (i)
        self.calc_result()
        self.write_result()
        self.close_all_files()

class CSVAverageCalcerMixin (object):
    out_def_fldnm = ['month','year','customer','average']
    wrk = {}

class CSVAvgClcWithNullAsNull (CSVAverageCalcerMixin, BaseCSVHandler):

    def __init__ (self, fnm_in='input.csv', fnm_out='output.csv', restkey=None, restval=None, dialect="excel", dateformat = '%d.%m.%Y', double_rec_is_error=True ):
        self.dateformat = dateformat
        self.double_rec_is_error = double_rec_is_error
        return BaseCSVHandler.__init__ (self, fnm_in, fnm_out, restkey, restval, dialect)

    def one_string_handler (self,s):
        print s
        csm = s['customer']
        if not csm in self.wrk:
            self.wrk[csm] = {}
        dt = datetime.strptime(s['date'],self.dateformat)
        mo_ye = str(dt.year)+str(dt.month).rjust(2,'0')
        if not mo_ye in self.wrk[csm]:
            self.wrk[csm][mo_ye]=[0 for i in range (monthrange(dt.year,dt.month)[1])]
        if not dt.day in self.wrk[csm][mo_ye]:
           self.wrk[csm][mo_ye][dt.day-1] = decimal.Decimal (s['money'])
        elif self.double_rec_is_errors:
            raise ValueError, \
                  ("incorrect input data - double records are found, customer -  %c, date - %d" %
                   csm, dt.strftime(self.dateformat))
        else:
            self.wrk[csm][mo_ye][dt.day-1] += Decimal (s['money'])
        print csm, mo_ye, self.wrk[csm][mo_ye][dt.day-1]

    def calc_result (self):
        min_mo_ye = '9'*6
        max_mo_ye = '0'*6
        for csm in self.wrk:
            for mo_ye in self.wrk[csm]:
                min_mo_ye = min (min_mo_ye, mo_ye)
                max_mo_ye = max (max_mo_ye, mo_ye)
                print csm, mo_ye
                print self.wrk [csm][mo_ye]
        print '--------------------'
        dt = datetime.strptime(min_mo_ye+'01',"%Y%m%d")
        end_dt = datetime.strptime(max_mo_ye+'20',"%Y%m%d")
        print dt, end_dt
        print '--------------------'
        while dt < end_dt:
            mo_ye = str(dt.year)+str(dt.month).rjust(2,'0')
            for csm in self.wrk:
                if mo_ye in self.wrk[csm]:
                    dct = {}
                    dct['month'] = str(dt.month).rjust(2,'0')
                    dct['year'] = str(dt.year)
                    dct['customer'] = csm
                    dct['average'] = str( round( sum (self.wrk[csm][mo_ye]) / len (self.wrk[csm][mo_ye]),2) )
                    print sum (self.wrk[csm][mo_ye])
                    self.result.append(dct)
                    print dct
                    print sum (self.wrk[csm][mo_ye]), ' | ',len (self.wrk[csm][mo_ye])
            dt += timedelta(days=monthrange(dt.year,dt.month)[1])
