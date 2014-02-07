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
            lvalue = float(left.data())
            rvalue = float(right.data())
        except TypeError:
            print left.data(), right.data()
        except ValueError:
            print left.data(), right.data()
        else:
            return lvalue < rvalue