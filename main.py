import math

from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QDialog, QGridLayout, QLabel, QComboBox, QSlider
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import preprocessing
import constants
import bubble_chart
import pandas as pd
import sys
import argparse


class Window(QDialog):

    def __init__(self, cfile: str, vfile: str, date: str, parent=None):
        super(Window, self).__init__(parent)
        try:
            self.community_df, self.hesitancy_df, self.date_data = preprocessing.process(cfile, vfile, date)
        except FileNotFoundError:
            print("Community or vaccine hesitancy dataset file not found. Aborting window initialization.")
            return

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.figure.set_size_inches(15.0, 7.0, forward=True)
        self.figure.set_dpi(150)

        self.layout = QGridLayout()

        # Set defaults
        self.size_attribute = 'SVI'
        self.svi_min_threshold = 0.1
        self.svi_max_threshold = 0.9
        self.population_threshold = 5000

        # Initialize bubble chart widgets
        self.size_dropdown, self.date_dropdown, \
            self.svi_min_slider, self.svi_min_label, \
            self.svi_max_slider, self.svi_max_label, \
            self.population_slider, self.population_label = self.initialize_bubble_widgets()

        self.setLayout(self.layout)
        self.overview_data = self.date_data
        self.bubblechart_plot()

    def initialize_bubble_widgets(self):

        # Title Label
        title = QLabel('COVID-19 Vaccine Hesitancy Visualization')
        title.setFont(QFont('Times', 18))

        # Size Attribute
        size_dropdown = QComboBox(self)
        size_dropdown.activated[str].connect(self.set_size)
        size_dropdown.addItems(constants.SIZE_ATTRIBUTES)
        size_dropdown.setCurrentIndex(0)

        # Date
        date_dropdown = QComboBox(self)
        date_dropdown.activated[str].connect(self.set_date)
        date_dropdown.addItems(constants.REPORT_DATES)
        date_dropdown.setCurrentIndex(0)

        # SVI Min Slider
        svi_min_slider = QSlider()
        svi_min_slider.setOrientation(QtCore.Qt.Horizontal)
        svi_min_slider.setMinimum(1)
        svi_min_slider.setMaximum(100)
        svi_min_slider.setSingleStep(5)
        svi_min_slider.setTickInterval(5)
        svi_min_slider.setValue(math.floor(self.svi_min_threshold * 100))
        svi_min_slider.setTickPosition(QSlider.TicksBelow)
        svi_min_slider.valueChanged.connect(self.set_min_svi)

        # SVI Min Slider Label
        svi_min_label = QLabel('Minimum SVI Threshold (' + str(self.svi_min_threshold) + '):')

        # SVI Max Slider
        svi_max_slider = QSlider()
        svi_max_slider.setOrientation(QtCore.Qt.Horizontal)
        svi_max_slider.setMinimum(1)
        svi_max_slider.setMaximum(100)
        svi_max_slider.setSingleStep(5)
        svi_max_slider.setTickInterval(5)
        svi_max_slider.setValue(math.floor(self.svi_max_threshold * 100))
        svi_max_slider.setTickPosition(QSlider.TicksBelow)
        svi_max_slider.valueChanged.connect(self.set_max_svi)

        # SVI Max Slider Label
        svi_max_label = QLabel('Maximum SVI Threshold (' + str(self.svi_max_threshold) + '):')

        # County Population Min Slider
        population_slider = QSlider()
        population_slider.setOrientation(QtCore.Qt.Horizontal)
        population_slider.setMinimum(1)
        population_slider.setMaximum(100)
        population_slider.setSingleStep(5)
        population_slider.setTickInterval(5)
        population_slider.setValue(math.floor(self.population_threshold / 1000))
        population_slider.setTickPosition(QSlider.TicksBelow)
        population_slider.valueChanged.connect(self.set_population)

        # County Population Label
        population_label = QLabel('Minimum County Population (' + str(self.population_threshold) + '):')

        # Build Layout
        self.layout.addWidget(title, 0, 0, 1, 2)
        self.layout.addWidget(self.canvas, 1, 0, 1, 4)

        self.layout.addWidget(QLabel('Size of Counties:'), 2, 2, 1, 2)
        self.layout.addWidget(size_dropdown, 3, 2, 1, 2)
        self.layout.addWidget(QLabel('Report Date:'), 4, 2, 1, 2)
        self.layout.addWidget(date_dropdown, 5, 2, 1, 2)

        self.layout.addWidget(svi_min_label, 2, 0, 1, 1)
        self.layout.addWidget(svi_min_slider, 3, 0, 1, 1)
        self.layout.addWidget(svi_max_label, 2, 1, 1, 1)
        self.layout.addWidget(svi_max_slider, 3, 1, 1, 1)
        self.layout.addWidget(population_label, 4, 0, 1, 2)
        self.layout.addWidget(population_slider, 5, 0, 1, 2)

        return size_dropdown, date_dropdown, svi_min_slider, svi_min_label, \
               svi_max_slider, svi_max_label, population_slider, population_label

    def set_size(self, text):
        self.size_attribute = text
        self.bubblechart_plot()

    def set_date(self, text):
        self.overview_data = preprocessing.process_date(self.community_df, self.hesitancy_df, text)
        self.bubblechart_plot()

    def set_min_svi(self, text):
        self.svi_min_threshold = text / 100.0
        self.svi_min_label.setText('Minimum SVI Threshold (' + str(self.svi_min_threshold) + '):')
        self.bubblechart_plot()

    def set_max_svi(self, text):
        self.svi_max_threshold = text / 100.0
        self.svi_max_label.setText('Maximum SVI Threshold (' + str(self.svi_max_threshold) + '):')
        self.bubblechart_plot()

    def set_population(self, text):
        self.population_threshold = text * 1000.0
        self.population_label.setText('Minimum County Population (' + str(self.population_threshold) + '):')
        self.bubblechart_plot()

    def bubblechart_plot(self):
        self.figure.clear()

        ax = self.figure.add_subplot(111)
        bubble_chart.plot(self.overview_data, ax, self.size_attribute,
                          self.svi_min_threshold, self.svi_max_threshold,
                          self.population_threshold)

        self.canvas.draw()


# If module is not being imported (ran as main program).
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CS 43900 Final Project')
    parser.add_argument('-c', action='store', required=True, dest='cfile')
    parser.add_argument('-v', action='store', required=True, dest='vfile')
    if len(sys.argv) == 5:
        namespace = parser.parse_args(sys.argv[1:])
        app = QApplication(sys.argv)
        main = Window(namespace.cfile, namespace.vfile, '2022-02-24')
        main.show()
        sys.exit(app.exec_())
    else:
        print('Usage: python main.py -c <community_file_path> -v <vaccine_file_path>')
