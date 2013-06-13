from csv import *

class MainCSVHandler (object):
    standart_fldnm = ['date','customer','money']

    def __init__ (self,fnm_in='input.csv', fnm_out='output.csv', restkey=None, restval=None,
                 dialect="excel" )
        self.f_in = open (fnm_in)
        self.csv_dict_reader = DictReader (self.f_in, restkey=restkey, restval=restval, dialect=dialect)
        fldnm = self.csv_dict_reader.fieldnames
        if len(fldnm) <> len (self.standart_fldnm):
            raise ValueError, \
                  ("incorrect number of columns in the file %f, it should have %n columns" %
                   fnm_in, len (self.standart_fldnm))
        else:
            chk = False
            l = ''
            for i in range (len(self.standart_fldnm)):
                chk = chk or fldnm[i]<>self.standart_fldnm[i]
                l += '"'+self.standart_fldnm[i]'", '
            if chk:
                raise ValueError, \
                  ("incorrect names of columns in the file %f, they should be (%s)" %
                   fnm_in, l[:len(l)-2])
        self.f_out = open (fnm_out, 'w')
        self.csv_dict_writer = DictWriter (self.f_out, dialect=dialect)