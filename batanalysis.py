# -*- coding: utf-8 -*-

###############################################################################
# Copyright (C), 2018, TP-LINK Technologies Co., Ltd.
#
# Author: wuyangbo_w9477
# History:
# 1, 2018-01-17, wuyangbo, first create:battery analysis tool
###############################################################################

import os
import re
import xlwt
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET


class Battery(object):
    '''store battery process data'''

    def __init__(self):
        '''create variable'''

        self.time = []
        self.voltage = []
        self.current = []
        self.temperature = []
        self.level = []
        self.vbus = []

    def data_len(self):
        '''calculate amount '''

        return len(self.time)

    def get_data(self, item_name):
        '''class attribute search interface'''

        return getattr(self, item_name)

    def add_data(self, item_name, value):
        '''add process data'''

        data_list = getattr(self, item_name)
        data_list.append(value)


def preprocess():
    '''get configuration from XML'''

    config_tree = ET.parse('config.xml')
    root = config_tree.getroot()
    regular_expression = root.find('RegularExpression').text

    record_name = []
    sequence = []
    plot_switch = []

    for record in root.iter('Record'):
        record_name.append(record.find('Name').text)
        sequence.append(int(record.find('Sequence').text))
        plot_switch.append(int(record.find('PlotSwitch').text))

    item_search_position = dict(zip(record_name, sequence))
    item_plot_switch = dict(zip(record_name, plot_switch))

    return regular_expression, item_search_position, item_plot_switch


def search_log(bat, regular_expression, item_search_position):

    try:
        log_name = raw_input('input log name(\'kernel_log\' by default): ')
        if not log_name:
            log_name = 'kernel_log'
        fp_log = open(log_name, 'r')
    except IOError, e:
        print 'could not open log file', e
        os._exit(0)

    # get data from log using regular expression
    is_first_item = True
    search_pattern = re.compile(regular_expression)
    for line in fp_log:
        charge_log = search_pattern.search(line)
        if charge_log is not None:
            for key in item_search_position.keys():
                temp = charge_log.group(item_search_position[key])
                if key == 'time':
                    t = float(temp)
                    if is_first_item:
                        init_t = t
                        is_first_item =  False
                    value = int(t - init_t)
                else:
                    value = int(temp)
                bat.add_data(key, value)
    fp_log.close()


def save_xls(bat, item_search_position):
    '''store process data in excel'''

    work_book = xlwt.Workbook()
    sheet = work_book.add_sheet('battery', cell_overwrite_ok=True)

    num = bat.data_len()
    for key in item_search_position.keys():
        sheet.write(0, item_search_position[key]-1, key)
        for count in range(num):
            temp = bat.get_data(key)[count]
            sheet.write(count+1, item_search_position[key]-1, temp)

    work_book.save('result.xls')


def save_pic(bat, item_plot_switch):
    '''plot data and save as png'''

    plt.style.use("ggplot")
    plt.figure(figsize=(24, 12))
    items_plot = []
    for key in item_plot_switch.keys():
        if cmp(key, 'time'):
            if item_plot_switch[key]:
                items_plot.append(key)
    sub_pic_num = len(items_plot)
    for count in range(sub_pic_num):
        item = items_plot[count]
        plt.subplot(sub_pic_num, 1, count+1)
        plt.plot(bat.get_data('time'), bat.get_data(item))
        plt.ylabel(item)
        plt.xlabel('Time')
        plt.grid(True)

    plt.subplots_adjust(hspace=0.4)
    plt.savefig('result.png')

if __name__ == '__main__':

    # get configuration from XML
    regular_expression, item_search_position, item_plot_switch = preprocess()
    bat = Battery()
    # get process data from log using regular expression
    search_log(bat, regular_expression, item_search_position)
    # save data in excel
    save_xls(bat, item_search_position)
    # plot data and save as png
    save_pic(bat, item_plot_switch)

