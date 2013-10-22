#!/usr/bin/env python
# coding: utf-8
'''
RiskFlow123D Postprocesor main module
'''

from PyQt4.QtGui import  QFont, QListWidgetItem, \
     QMainWindow, QApplication, QFileDialog, QStatusBar,\
     QTableWidgetItem, QIntValidator, QDoubleValidator, QSortFilterProxyModel, QStandardItemModel,\
     QStandardItem

from PyQt4.QtCore import Qt


from iniparse import INIConfig
from multiprocessing import Process, Queue, cpu_count, freeze_support     
from flowIni import flow, material, mesh, transport, surface
from genericpath import exists
from helpers import logger, grafLinear, csvexport, ruzne, concentrations, merger
from ui_postprocess import Ui_MainWindow
from os import mkdir, listdir, path
import sys


__version__ = '0.0.2'
__appname__ = 'RiskFlow123D-post'
__inifile__ = './riskflow123d-post.ini'


SEPAR = '/'
METHODS = ('Basic Problem', 'Monte Carlo', 'Sensitivity Task')
IDSDICT = {'basicProblem':'analyse_basic_problem', 'MonteCarlo':'analyse_monte_carlo', 'Sensitivity':'analyse_sensitivity_task'}
AXIS_TRANS = {'x':0, 'y':1, 'z':2}
DATA_FORMAT = 'json'
FNAME_SURF = 'surface.txt'
FNAME_MERGE = 'merged_concentrations.csv'
FNAME_ELEMS = transport.FNAME_ELEMS + '.' + transport.FNAME_EXT[DATA_FORMAT]
FNAME_TIME = transport.FNAME_TIME + '.' + transport.FNAME_EXT[DATA_FORMAT]
FNAME_SUMA = transport.FNAME_SUMA + '.' + transport.FNAME_EXT[DATA_FORMAT]
TAB_LABELS = ['task number', 'sum of concentrations', 'grade']

class NumberSortModel(QSortFilterProxyModel):

    def lessThan(self, left, right):
        try:
            lvalue = float(left.data())
            rvalue = float(right.data())
        except TypeError:
            print left.data(), right.data()
        except ValueError:
            print left.data(), right.data()    
        else:    
            return lvalue < rvalue


class MainWindow(QMainWindow, Ui_MainWindow):
    '''
    Main app window
    '''
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        
        #promenne
        self.work_dir = ''
        self.master_work_dir = ''
        self.logovat = False
        self.flowini_file_master = ''
        self.flowini_data = ''
        self.file_dict = ''
        self.displayed_mesh_list = {}
        self.displayed_mtr_list = {}
        self.result_elements = None
        self.result_times = None
        self.surface_elements = None
        self.comparation_table = None
        self.material = None
        self.mtr_index_disp_lst = {}
        self.logger = None
        self.msh = None
        self.tasks = None
        self.solutions = None
        self.problem_type = None
        
        #setup app
        self.setup = None
        self._load_setup()
        
        #toolbar
        self.__setup_toolbar()
        #status bar
        self.status_bar = None
        self.__setup_statusbar()
        #mesh control
        self.__setup_mesh_control()
        #misc
        self.button_compare.clicked.connect(self.compare_concentrations)
        self.check_compare_sum.setChecked(True)
        self.button_export_csv.clicked.connect(self.export_compare_conc)
        self.button_export_csv.setDisabled(True)
        self.spin_grade_filter.setRange(0, 5)
        self.spin_grade_filter.setDisabled(True)
        self.button_grade_filter.setDisabled(True)
        self.button_grade_filter.clicked.connect(self.__filter_table_rslt)      
        
        
        #progress bar
        self.tabWidget.currentChanged.connect(self._tab_controller)
        self.button_process_all.clicked.connect(self._analyze_data)
        self.button_process_newonly.clicked.connect(self._analyze_data_selected)
        
        #na zacatku neni nic
        self.tabWidget.hide()
        self.tabWidget.removeTab(1)
        self.tabWidget.removeTab(1)
        
    def __setup_statusbar(self):
        '''
        status bar setup - private method 
        '''
        #status bar
        status_font = QFont("Helvetica [Cronyx]", 12)
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.setFont(status_font)     
        
    def __setup_toolbar(self):
        '''
        toolbar setup
        '''
        #toolbar
        self.button_exit.clicked.connect(self.close)
        self.button_draw_charts.clicked.connect(self.draw_charts)
        self.button_save_tables.clicked.connect(self.create_tables)
        self.button_quick_test.clicked.connect(self.load_test)
        
        self.button_merge.clicked.connect(self.merge_result_files)
        self.box_merger.setHidden(True)
        
        float_validator = QDoubleValidator()
        self.edit_merge_minval.setValidator(float_validator)
        
        self.action_Open.triggered.connect(self.open_task_dir)
        self.action_Basic_problem.triggered.connect(self.analyse_basic_problem)
        self.actionSensitivity_task.triggered.connect(self.analyse_sensitivity_task)
        self.actionMonte_Carlo.triggered.connect(self.analyse_monte_carlo)    
    
    def __setup_mesh_control(self):
        '''
        setup for mesh control block
        '''
        #mesh control
        self.button_mesh_imp_surface.clicked.connect(self._mesh_import_surface)
        self.button_mesh_imp_nonzero.clicked.connect(self._mesh_import_nonzero)
        self.button_mesh_import_all.clicked.connect(self._mesh_import_all)
        self.button_mesh_remove_all.clicked.connect(self._mesh_remove_all)
        self.button_mesh_import_mtr.clicked.connect(self._mesh_import_mtr)
        self.button_mesh_remove_mtr.clicked.connect(self._mesh_remove_mtr)
        self.button_mesh_imp_over.clicked.connect(self._mesh_import_over)
        self.button_mesh_imp_bellow.clicked.connect(self._mesh_import_bellow)
        self.button_mesh_rem_over.clicked.connect(self._mesh_remove_over)
        self.button_mesh_rem_bellow.clicked.connect(self._mesh_remove_bellow)
        self.button_mesh_imp_through.clicked.connect(self._mesh_import_through)
        self.button_mesh_rem_through.clicked.connect(self._mesh_remove_through)
        self.button_mesh_imp_elmid.clicked.connect(self._mesh_import_id)
        self.button_mesh_rem_elmid.clicked.connect(self._mesh_remove_id)
        self.mesh_list.itemClicked.connect(self._mesh_element_explorer_control)
        self.mesh_radio_z.setChecked(True)
        self.button_mesh_remove_zero.clicked.connect(self._mesh_remove_zero)
        
        integer_validator = QIntValidator()
        self.mesh_element_id_edit.setValidator(integer_validator)
        self.edit_mesh_crd.setValidator(integer_validator)
            
        
    def load_test(self):
        '''function for quick test'''
        if len(self.work_dir) <= 2:
            self.work_dir = '../data/test_melechov/MonteCarlo/02'
        self.identify_problem_type()
        self.tabWidget.setCurrentIndex(2)
        
    def export_compare_conc(self):
        '''
        method for export comparsion table to csv file
        comparation has to be done first 
        '''
        if not self.comparation_table:
            self.messenger('export error - data not exists')  
            return False
            
        csvexport.write_comparsion_tab(self.comparation_table, self.work_dir)
        self.messenger('Table has been successfully exported to CSV file')
        self.button_export_csv.setDisabled(True)     
    
    def compare_concentrations(self):
        '''
        method for concentration comparsion 
        check what list and method has to be used
        '''
        if self.radio_compare_all.isChecked():
            self.__compare_selected_conc()
        elif self.radio_compare_selected.isChecked():
            self.__compare_selected_conc(self.displayed_mesh_list.keys())
        elif self.radio_compare_surface.isChecked():
            if not self.surface_elements:
                fname = self.work_dir + '/' + 'master/' + FNAME_SURF
                self.surface_elements = surface.read_result(fname) 
            self.__compare_selected_conc(self.surface_elements)
            
    def merge_result_files(self):
        '''
        Method for merging result files 
        parses all task dirs, opens result json files and merge values to one big table
        discards results in master dir
        '''
        merged_table = {}
        conc = transport.parse_task_dirs(self.work_dir, FNAME_ELEMS)
        
        minval = self.edit_merge_minval.text()
        
        try:
            minval = float(minval)
        except ValueError:
            minval = 0.0   
        
        for fname in conc:
            elem_conc = transport.load_vysledek(fname)
            if not 'master' in fname:
                for elid, time_dict in elem_conc.items():
                    if merged_table.has_key(elid):
                        merged_table[elid].append(time_dict)
                    else:
                        merged_table[elid] = [time_dict, ]
            else:
                master_conc = elem_conc
                
           
        output_file = self.work_dir + SEPAR + FNAME_MERGE
        self.messenger('Merging the results to one file / it may take a while...')
        merger.table_to_file(merged_table, master_conc, output_file,  len(conc)-1, minval)
        self.messenger('Data has been successfully merged and exported to CSV file')
                    
    

                        
            
    def __compare_selected_conc(self, elm_list = None):
        '''
        wrapper for selected method
        parses all dirs and sums concentrations for all/selected elements
        output a table with sum 
        '''
         
        master = self.work_dir + '/' + 'master/' + FNAME_SUMA
        mas_conc_suma =  transport.load_vysledek(master)
        mas_total = concentrations.sum_conc(mas_conc_suma, elm_list)
        
        
        list_of_conc = []
        task_numbers = []
        conc = transport.parse_task_dirs(self.work_dir, FNAME_SUMA)
        for fname in conc:
            conc_suma = transport.load_vysledek(fname)
            task_nr = path.split(fname)[0]
            task_name = task_nr.split('\\')[-1]
            if task_name == 'master':
                task_name = '9999999'
            task_numbers.append(task_name)
            list_of_conc.append(concentrations.sum_conc(conc_suma, elm_list))
        
        grade_vector = concentrations.grade_result(mas_total, list_of_conc)
        table_rows = zip(task_numbers, list_of_conc, grade_vector)
        table_rows = sorted(table_rows, key = lambda grade: grade[2], reverse=True)
                
        self.__display_table_rslt(table_rows)
        #enable export
        self.comparation_table = table_rows
        self.button_export_csv.setEnabled(True)
        self.spin_grade_filter.setEnabled(True)
        self.button_grade_filter.setEnabled(True)      
        
    def __display_table_rslt(self, table_rows):
        '''
        controls table_comp_rslt widget
        fill the widget with table_rows list
        @param table_rows: []  
        '''
       
        
        rows_count = len(table_rows) 
        model = QStandardItemModel(rows_count, 3)
        
        model.setHorizontalHeaderLabels(TAB_LABELS)
        
        #fill model with data
        for row in range(rows_count):
            for col in range(3):
                item = QStandardItem()
                item.setData(str(table_rows[row][col]), Qt.DisplayRole)
                model.setItem(row, col, item)
        
        #self.table_comp_rslt.clearContents()
        if self.table_comp_rslt.isSortingEnabled():
            self.table_comp_rslt.setSortingEnabled(False)    
        
        proxy = NumberSortModel()
        proxy.setSourceModel(model)
        self.table_comp_rslt.setModel(proxy)
        self.table_comp_rslt.resizeColumnsToContents()
        self.table_comp_rslt.setSortingEnabled(True)
        
    def __filter_table_rslt(self):
        '''
        filter for grades
        '''
        grval = int(self.spin_grade_filter.value())
        newtab = [(elm, conc, grade) for (elm, conc, grade) in self.comparation_table if ((grade >= grval) or (elm == '9999999'))]
                    
        self.__display_table_rslt(newtab)
        
        
    def _tab_controller(self):    
        '''
        controlling index of tab widget and throw action
        signal: tabWidget index change
        '''
        actions = {
                   'tab_4' : '_data_dialog',
                   'tab_1' : '_analyser_dialog',
                   }
        idx = self.tabWidget.currentWidget().objectName()
        print idx
        if actions.has_key(idx):
            getattr(self, actions[idx])()
        
    def _analyser_dialog(self):
        '''
        a dialog for analyser screen
        '''
        
        ptr = self.tabWidget.currentWidget().objectName()
        if ptr == 'tab_1':
            if not self.result_elements:
                self.read_concentrations()
            
            msg = 'found {} elements with non-zero concentration'.format(len(self.result_elements))    
            self.label_basic_1.setText(msg)
            msg = '{} selected by element selector for drawing'.format(len(self.displayed_mesh_list))
            self.label_basic_2.setText(msg)
            
            
    def _data_dialog(self):
        '''
        a dialog for data processing
        '''
        self.progress_processing.setHidden(True)
        self.progress_processing.setMinimum(0)
        self.progress_processing.setValue(0)
        
        self.tasks = transport.get_result_files(self.work_dir)
        n_tas = len(self.tasks)
        
        self.solutions = transport.parse_task_dirs(self.work_dir, FNAME_ELEMS)
        n_sols = len(self.solutions)
        
        if n_tas-n_sols == 0:
            self.button_process_newonly.setHidden(True)
            self.button_process_all.setText('Start')
        else:
            self.button_process_newonly.setVisible(True)
            self.button_process_all.setText('All')    
        
        msg = "Found {} tasks to analyze. That will take approx. {}\n".format(n_tas, ruzne.format_time(n_tas*4))
        msg += "{} tasks was already processed (compressed file found), {} still need processing".format(n_sols, n_tas-n_sols)
        self.label_processing_text.setText(msg)
        
        self.progress_processing.setMaximum(n_tas*4)
    
    def _analyze_data(self):
        '''
        action for button_process_all
        takes all tasks in work_dir to process
        '''
        if not self.tasks:
            self.tasks = transport.get_result_files(self.work_dir)
        
        self.messenger('Processing data, it may take a while')    
        self._analyze_data_routine(self.tasks)
        self.messenger('Processing successfully finished', 300)
        self._data_dialog()
        
    def _analyze_data_selected(self):
        '''
        action for button_process_newonly
        takes only unprocessed tasks in work_dir to process
        '''
        if not self.tasks:
            self.tasks = transport.get_result_files(self.work_dir)
        if not self.solutions:
            self.solutions = transport.parse_task_dirs(self.work_dir, FNAME_ELEMS)
            
        dir1 = [path.split(sol)[0] for sol in self.solutions]
        dir2 = [path.split(sol)[0] for sol in self.tasks]
        unproc_list = [transport.get_result_files(i)[0] for i in dir2 if i not in dir1]
        
        self.messenger('Processing data, it may take a while')
        self._analyze_data_routine(unproc_list)
        self.messenger('Processing successfully finished', 300)
        self._data_dialog()
        
    def _analyze_data_routine(self, task_list):
        '''
        analyze transport out data
        uses transport_multi module for multiprocess computation
        '''
        nr_of_proc = cpu_count()
        self.progress_processing.setMaximum(len(task_list)*4)
        self.progress_processing.setVisible(True)
        
        # Create queues
        task_queue = Queue()
        done_queue = Queue()
        #populate queue with data
        for result in task_list:
            task_queue.put(result)
        #Start worker processes
        for _11 in range(nr_of_proc):
            Process(target=transport.worker, args=(task_queue, done_queue)).start()
        # Get and print results
        nval = 0
        for _12 in range(len(task_list)):
            nval = nval + done_queue.get()
            self.progress_processing.setValue(nval)       
        
        self.progress_processing.setMaximum(nval)
        # Tell child processes to stop
        for _13 in range(nr_of_proc):
            task_queue.put('STOP')
            
    def draw_charts(self):
        '''
        Draw charts 
        apply filter of displayed list if any
        if not draw for all non-zero elements
        
        '''
        if not self.result_elements:
            self.read_concentrations()
        
        self.messenger('Data loaded sucessfully, starting drawing the charts')   
        
        gdir = self.work_dir+'/charts/'
        if not exists(gdir):
            mkdir(gdir)
        
        if len(self.displayed_mesh_list) > 0:
            filtered_dict = grafLinear.list_filter(self.result_elements, self.displayed_mesh_list.keys())
        else:
            filtered_dict = self.result_elements    
        
        for xkey, xval in filtered_dict.items():
            disp = grafLinear.fill_up_zeros(self.result_times, xval)
            grafLinear.draw_chart(xkey, self.result_times, disp, gdir)
            self.messenger('chart for element {} created'.format(xkey))
            
        self.messenger('all charts sucessfully created')
        
    def create_tables(self):
        '''Create csv table with results'''
        if not self.result_elements:
            self.read_concentrations()
            
        csvexport.write_single_conc_tab(self.result_elements, self.result_times, self.work_dir) 
        self.messenger('table of concentrations created') 
        
        
        
    def read_concentrations(self, fname=None):
        '''read concentration from TransportOut result file'''
        if fname == None:
            fname = self.master_work_dir+SEPAR+self.file_dict['Transport_out']
            
        print self.master_work_dir
        self.result_elements = transport.load_vysledek(self.master_work_dir + SEPAR + FNAME_ELEMS)  
        self.result_times = transport.load_vysledek(self.master_work_dir + SEPAR + FNAME_TIME)
        if not self.result_elements and not self.result_times:
            self.messenger('Did not find results data, start processing')  
            self.result_times, self.result_elements =  transport.read_transport(fname)
            transport.save_vysledek(self.work_dir + SEPAR + FNAME_ELEMS, self.result_elements) 
            transport.save_vysledek(self.work_dir + SEPAR + FNAME_TIME, self.result_times)    
        
    def start_logger(self):
        '''
        logging tool startup
        '''
        self.logger = logger.get_it(__appname__, '{}{}.log'.format(self.output_dir, __appname__.lower())) 
        self.logovat = True    
        
    def messenger(self, msg, dtime=0):
        '''sending messages to status bar, and to log, if it's enabled'''    
        self.status_bar.showMessage(msg, dtime)
        if self.logovat:
            self.logger.info(msg)
            
    def init_mesh_tools(self):
        '''
        mesh tools starter
        '''
        self._load_msh()
        self._load_mtr()
        self._load_surface()
        self._fill_mesh_mtr_form()
        self.messenger('MESH tools successfully loaded all data', 8000)
        self._analyser_dialog()
        
        self.tabWidget.show()            
        
    def analyse_basic_problem(self):
        '''
        action for basic analyser
        '''
        self.master_work_dir = self.work_dir + '/'
        self.problem_type = 'basic'
        if self.find_and_open_inifile():
            self.box_merger.setHidden(True)
            self.tabWidget.removeTab(2)
            self.tabWidget.addTab(self.tab_2,'Basic Analyser')
            self.init_mesh_tools() 
            self.tabWidget.setCurrentIndex(2)
            self._save_setup()
        
    def analyse_sensitivity_task(self):
        '''
        action for sensitivity analyser
        '''
        self.master_work_dir = self.work_dir + '/master/'
        self.problem_type = 'compare'
        if self.find_and_open_inifile():
            self.box_merger.setHidden(True)
            self.tabWidget.removeTab(2)
            self.tabWidget.addTab(self.tab_3,'Sensitivity Analyser')
            self.label_analyser_title.setText('Sensitivity Analyser')
            self.init_mesh_tools()  
            self.tabWidget.setCurrentIndex(2)
            self._save_setup()
        
    def analyse_monte_carlo(self):
        '''
        action for monte carlo analyser
        '''
        self.master_work_dir = self.work_dir + '/master/'
        self.problem_type = 'compare'
        
        if self.find_and_open_inifile():
            self.tabWidget.removeTab(2)
            self.tabWidget.addTab(self.tab_3,'Monte Carlo Analyser')
            self.label_analyser_title.setText('Monte Carlo Analyser')
            self.init_mesh_tools()  
            
            self.box_merger.setHidden(False)
            self.tabWidget.setCurrentIndex(2)
            self._save_setup()         
        
        
    def open_task_dir(self):
        '''SetUP output using Qfiledialog'''        
        adr = "."
        tmp = QFileDialog.getExistingDirectory(self, "Open output directory", adr, options=QFileDialog.ShowDirsOnly)
        if ruzne.isit_task_folder(tmp): 
            self.work_dir = tmp
            self.identify_problem_type() 
        else: self.messenger('ERROR: Selected directory does not contain problem.type file!')
        
    def identify_problem_type(self):
        '''
        search dir for file problem.type 
        fails if file not exist
        '''
        try:
            rfile = open(self.work_dir + '/problem.type')
        except IOError:
            self.messenger('ERROR: failed to open problem.type file') 
        else:
            istr = rfile.read()
            if istr.strip() in IDSDICT.keys():
                func = getattr(self, IDSDICT[istr.strip()])
                func()
            else:
                self.messenger('ERROR: failed to recognize given problem')                     
        
    
    
    def find_and_open_inifile(self):
        '''search work dir for a flow ini to open it'''
        
        list_of_files = [ff for ff in listdir(self.master_work_dir) if ff.lower().endswith('ini')]
        
        if not list_of_files: 
            self.messenger('ERROR: no ini files found, failed to continue')
            return False
        elif len(list_of_files) > 2: 
            self.messenger('ERROR: 2 or more ini files found, failed to continue')
            return False
        else:
            self.flowini_file_master = list_of_files[0].strip()
            fname = self.master_work_dir + self.flowini_file_master
            self.file_dict = flow.getDictFromFile(fname) 
            return True

    def _load_setup(self):
        '''load setup, create a new file if not exists'''
        try:
            fread = open(__inifile__)
            self.setup = INIConfig(fread)
            self.work_dir = self.setup['Work']['Dir']
            fread.close()
        
        except IOError:
            setup = "[Work]\nDir = ''\n"  
            fnew = open(__inifile__,'w')
            print >> fnew, setup
            fnew.close()
            
            
    
    def _save_setup(self):
        '''saves ini file'''
        self.setup['Work']['Dir'] = self.work_dir
        fnew = open(__inifile__,'w')
        print >> fnew, self.setup
        fnew.close()
            

    def _load_surface(self, file_name=None):
        '''
        load surface elems using surface module
        first try to open prepared file, in case of file create a new one using surface module
        '''
        wdir = {'basic' : self.work_dir, 'compare' : self.master_work_dir} 
        
        
        if file_name is None: 
            fname = self.master_work_dir + FNAME_SURF
            
        self.messenger('Loading Surface elements') 
        if path.isfile(fname):
            self.surface_elements = surface.read_result(fname)
        else:
            fname_bcd = wdir[self.problem_type] + '/' + self.file_dict['Boundary']
            fname_msh = wdir[self.problem_type] + '/' + self.file_dict['Mesh']
            self.surface_elements = surface.read(fname_bcd, fname_msh)
            surface.write(fname, self.surface_elements)
                
        self.messenger('Surface elements successfully loaded', 8000)     
    
    def _load_msh(self, file_name=None):
        '''
        load mesh using mesh module
        '''
        if file_name is None: 
            file_name = self.master_work_dir + self.file_dict['Mesh']
                       
        self.messenger('Loading MSH') 
        self.msh = mesh.Mesh()
        self.msh.read(file_name)
        self.messenger('MSH successfully loaded', 8000) 
        
    def _load_mtr(self, file_name=None):
        '''load mtr from file, if not given look to the flow.ini settings'''
        if file_name == None: 
            file_name = self.master_work_dir + '/' + self.file_dict['Material']
        
        self.messenger('Loading materials from MTR file')  
        self.material = material.Material()
        self.material.getDictFromFile(file_name)
        self.messenger('MTR successfully loaded', 8000) 
        
    def _fill_mesh_mtr_form(self):
        '''fill form in the mesh editor'''
        self.select_mesh_mtr.clear()
        wherefrom = self.msh.mtr_index.keys()
        data = ["%s" % str(k) for k in sorted(wherefrom)]
        self.select_mesh_mtr.insertItems(0, data)
        self.select_mesh_mtr.repaint()
        
    def _mesh_element_explorer_control(self):
        '''
        action for controlin mesh_element_explorer display block
        '''
        idxtu = str(self.mesh_list.currentIndex().data().toString())
        idx, typ, mat = idxtu.split()
        del(typ)
        del(mat)
        doc = "element id: {0}\n".format(idx)
        doc += "node : [x, y, z]\n"
        for node in self.msh.elements[int(idx)][2]:
            doc +=  "{0} : {1}\n".format(node, self.msh.nodes[node])
        self.mesh_element_explorer.clear()
        self.mesh_element_explorer.insertPlainText(doc)
        self.mesh_element_explorer.setReadOnly(True)    
        
    def _mesh_import_list_updater(self, vals=None, todisp=0):
        '''helper for various list update functions
        @PARAM vals {mesh elements}
        @PARAM todisp number of elements for message
        '''
        if vals is not None and len(vals) > 0 : 
            self.displayed_mesh_list.update(vals)
            todisp = len(vals)
            msg = 'Loading %s elements to the list. It may take a while...' % str(todisp)
            self.messenger(msg)
            self._mesh_list_refresh()
            self.messenger('Selection of elements loaded', 8000)
        
    def _mesh_import_list_deleter(self, vals):
        '''
        deletes given values from displayed mesh list
        @param vals: {} of values to be deleted 
        '''
        for key in vals.keys():
            try:
                del(self.displayed_mesh_list[key])
            except KeyError:
                pass
                  
        msg = 'Refreshing the list'
        self.messenger(msg)
        self._mesh_list_refresh()
        self.messenger('Refreshing finished', 8000)
        
    def _get_mesh_axis(self):
        '''
        check what radio is checked, return axis
        @return: axis string identifier
        '''
        if self.mesh_radio_x.isChecked():
            return 'x'
        elif self.mesh_radio_y.isChecked():
            return 'y'
        elif self.mesh_radio_z.isChecked():
            return 'z'
        else:
            self.messenger('Choose axis first!', 8000)
            return False             
        
    def _mesh_import_surface(self):    
        '''
        imports surface elements to mesh list
        need surface_result file to work
        '''
        
        if not self.surface_elements:
            fname = self.work_dir + '/' + 'master/' + FNAME_SURF
            self.surface_elements = surface.read_result(fname) 
                
        vals = {}
        for elid in self.surface_elements:
            elid = int(elid)
            if self.msh.elements.has_key(elid):
                vals[elid] = self.msh.elements[elid]
            
        self._mesh_import_list_updater(vals)
        
    def _mesh_remove_zero(self):
        '''
        removes elemtns with no (zero values) concentration in time from mesh list
        '''
        if not self.result_elements:
            self.read_concentrations()
        
        for key in self.displayed_mesh_list.keys():
            if str(key) not in self.result_elements:
                del(self.displayed_mesh_list[key])
        
        msg = 'Refreshing the list'
        self.messenger(msg)
        self._mesh_list_refresh()
        self.messenger('Refreshing finished', 8000)                     
    
    def _mesh_import_nonzero(self):
        '''
        imports elements with nonzero concentration in time to mesh list
        '''
        if not self.result_elements:
            self.read_concentrations()
            
        vals = {}
        for elid in self.result_elements:
            elid = int(elid)
            if self.msh.elements.has_key(elid):
                vals[elid] = self.msh.elements[elid]
            
        self._mesh_import_list_updater(vals)       
        
        
    def _mesh_import_axis(self, compare, axis = 'z'):
        '''import elements with coordinate in given axis, 
           compare given val with the value of mesh spinbox
        @param compare: -1 for elements bellow, 0 for through, 1 for over 
        @param axix: what axis (x, y, z)
        '''
        val = int(self.edit_mesh_crd.text())
        vals = {}
        for elid, elem in self.msh.elements.items():
            pridat = True
            for node_id in elem[2]:
                node_coord = self.msh.nodes[node_id][AXIS_TRANS[axis]]
                if cmp(node_coord, val) == compare or cmp(node_coord, val) == 0 :
                    pridat = False
            if pridat:
                vals[elid] = self.msh.elements[elid]
        
        return vals
        
    def _mesh_find_through(self, axis = 'z'):
        '''import elements with at last one node over coordinate in given axis,
           such elements has to be cuted through given plane
           compare given val with the value of mesh spinbox
        @param axix: what axis (x, y, z)
        '''
        val = int(self.edit_mesh_crd.text())
        
        vals = {}
        for elid, elem in self.msh.elements.items():
            nad = False
            pod = False
            for node_id in elem[2]:
                node_coord = self.msh.nodes[node_id][AXIS_TRANS[axis]]
                if cmp(node_coord, val) == 1 or cmp(node_coord, val) == 0 :
                    nad = True
                elif cmp(node_coord, val) == -1 or cmp(node_coord, val) == 0 :
                    pod = True
            if nad and pod:
                vals[elid] = self.msh.elements[elid]
        return vals        
    
    def _mesh_import_through(self):
        '''import elements where one node has Z over value of mesh spinbox
        and therefore this element is cut by given alt
        '''
        axis = self._get_mesh_axis()
        if axis:
            vals = self._mesh_find_through(axis)
            self._mesh_import_list_updater(vals)
        
    def _mesh_import_over(self):
        '''import elements where all nodes has Z over value of mesh spinbox
        '''
        axis = self._get_mesh_axis()
        if axis:
            vals = self._mesh_import_axis(-1, axis)
            self._mesh_import_list_updater(vals)
        
    def _mesh_import_bellow(self):
        '''import elements where all nodes has Z bellow value of mesh spinbox
        '''
        axis = self._get_mesh_axis()
        if axis:
            vals = self._mesh_import_axis(1, axis)
            self._mesh_import_list_updater(vals)
            
    def _mesh_import_id(self):
        '''
        Import elemet with id given in form 
        and update displayed list
        '''
        try:
            elmid = int(self.mesh_element_id_edit.text())
            vals = {elmid : self.msh.elements[elmid]}
            self._mesh_import_list_updater(vals)
        except KeyError:
            self.messenger('ERROR: no such element', 8000)
        except ValueError:
            self.messenger('ERROR: not valid element id', 8000)       
    
    def _mesh_remove_id(self):
        '''
        Remove elemet with id given in form  
        and update displayed list
        '''
        elmid = int(self.mesh_element_id_edit.text())
        try:
            vals = {elmid : self.msh.elements[elmid]}
            self._mesh_import_list_deleter(vals)
        except KeyError:
            self.messenger('ERROR: no such element', 8000)                
        
    def _mesh_remove_over(self):
        '''removes elements where all nodes has coordinate in axis
         over value of mesh spinbox
        '''
        axis = self._get_mesh_axis()
        if axis:
            vals = self._mesh_import_axis(-1, axis)
            self._mesh_import_list_deleter(vals)               
        
    def _mesh_remove_bellow(self):
        '''
        removes elements with coordinate in given axis
        bellow value of mesh spinbox
        '''
        axis = self._get_mesh_axis()
        if axis:
            vals = self._mesh_import_axis(1, axis)
            self._mesh_import_list_deleter(vals)
        
    def _mesh_remove_through(self):
        '''
        removes elements cuted through by given plane
        '''
        
        axis = self._get_mesh_axis()
        if axis:
            vals = self._mesh_find_through(axis)
            self._mesh_import_list_deleter(vals)           
        
    def _mesh_import_mtr(self):
        '''import all nodes with material selected in the selec_mtr_mesh'''
        idx = int(self.select_mesh_mtr.currentText())
        vals = {}
        for i in self.msh.mtr_index[idx]:
            vals[i] = self.msh.elements[i] 
    
        self._mesh_import_list_updater(vals)
            
    def _mesh_remove_mtr(self):
        '''delete all nodes with material selected in the selec_mtr_mesh'''
        idx = int(self.select_mesh_mtr.currentText())
        for i in self.msh.mtr_index[idx]:
            del self.displayed_mesh_list[i] 
        
        msg = 'Deleting %s elements from the list. It may take a while...' % str(len(self.msh.mtr_index[idx]))
        self.messenger(msg)
        self._mesh_list_refresh()
        self.messenger('Selection of elements loaded', 8000)
            
            
    def _mesh_import_all(self):
        '''imports all mesh to list - msh file need to be loaded first'''
        try:
            msg = 'Loading %s elements to the list. It may take a while...' % str(len(self.msh.elements))
            self.messenger(msg) 
            self.displayed_mesh_list = self.msh.elements.copy()
            self._mesh_list_refresh()
            self.messenger('MSH data loaded', 8000)
        except AttributeError:
            self.messenger('Error: load MSH data first!', 8000)
            
    def _mesh_remove_all(self):
        '''
        Clear mesh selected list completely 
        '''
        try:
            self.displayed_mesh_list = {}
            self.mesh_list.clear()
        finally:
            self.messenger('Data removed from list', 8000)
            self.groupBox_2.setTitle('0 elements in the list')
            
    def _mesh_list_refresh(self):
        '''
        takes actual dict self.displayedList and refresh the view
        displays - element id, element type, material
        
        creates and refreshes dict of mtr {mtrid : [el1, el2]} 
        '''
        try:
            self.mesh_list.clear()
            self.mtr_index_disp_lst = {}
            
            for key in sorted(self.displayed_mesh_list.keys()):
                #update of list
                mtr = self.displayed_mesh_list[key][1][0]
                tst = "%s %s %s" % (key, self.displayed_mesh_list[key][0], mtr) 
                QListWidgetItem(str(tst), self.mesh_list)
                #update of index
                if self.mtr_index_disp_lst.has_key(mtr):
                    self.mtr_index_disp_lst[mtr].append(key)
                else:
                    self.mtr_index_disp_lst[mtr] = [key]    
           
            #update the default index
            self.msh.mtr_index.update(self.mtr_index_disp_lst)                     
            self.mesh_list.repaint()
            msg = "{0} elements in the list".format(len(self.displayed_mesh_list))
            self.groupBox_2.setTitle(msg)
            
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise            
            
        
if __name__ == '__main__':
    freeze_support()
    APP = QApplication(sys.argv)
    FRAME = MainWindow()
    FRAME.show()    
    APP.exec_()
            