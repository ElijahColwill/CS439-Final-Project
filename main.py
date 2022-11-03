from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QDialog, QGridLayout, QLabel
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import preprocessing
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

        title = QLabel('COVID-19 Vaccine Hesitancy Visualization')
        title.setFont(QFont('Times', 18))

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.figure.set_size_inches(15.0, 7.0, forward=True)
        self.figure.set_dpi(150)

        self.layout = QGridLayout()

        self.layout.addWidget(title, 0, 0, 1, 2)
        self.layout.addWidget(self.canvas, 1, 0, 1, 4)

        self.setLayout(self.layout)
        self.overview_data = self.date_data
        self.bubblechart_plot('Percent White')

    def bubblechart_plot(self, size_attribute: str):
        self.figure.clear()

        ax = self.figure.add_subplot(111)
        bubble_chart.plot(self.date_data, ax, size_attribute)

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
