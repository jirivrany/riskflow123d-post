# coding: utf-8
from PyQt4.QtGui import QSortFilterProxyModel

class NumberSortModel(QSortFilterProxyModel):
    '''
    sorting model for table
    '''
    def lessThan(self, left, right):
        '''
        compare method
        '''
        try:
            lvalue = left.data().toFloat()
            rvalue = right.data().toFloat()
        except TypeError:
            print "table data comparsion TypeError / failed convert to float"
        except ValueError:
            print "table data comparsion ValueError / failed convert to float"
        else:
            return lvalue < rvalue