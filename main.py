import argparse
import math
import sys

from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QDialog, QGridLayout, QLabel, QComboBox, QSlider, QPushButton
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from preprocessing import preprocessing
from visualizations import bubble_chart, map, stream_graph, constants


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
        self.attribute_key = 'Cases Per 100k'
        self.state = 'Country View'
        self.secondary = 'None'
        self.stream_attribute = 'Community Level'
        self.view = 'County'

        # Initialize bubble chart widgets
        self.size_dropdown, self.size_label, self.svi_min_slider, self.svi_min_label, \
            self.svi_max_slider, self.svi_max_label, self.population_slider, \
            self.population_label = self.initialize_bubble_widgets()

        self.bubble_widgets = [self.size_dropdown, self.size_label, self.svi_min_slider,
                               self.svi_min_label, self.svi_max_slider, self.svi_max_label,
                               self.population_slider, self.population_label]

        # Initialize map widgets
        self.attribute_dropdown, self.attribute_label, self.date_dropdown, self.date_label, \
            self.state_dropdown, self.state_label, self.attribute_secondary_dropdown, \
            self.attribute_secondary_label, self.county_btn, self.state_btn = self.initialize_map_widgets()

        self.primary_map_widgets = [self.attribute_dropdown, self.attribute_label, self.date_dropdown,
                                    self.date_label, self.state_dropdown, self.state_label]

        self.secondary_map_widgets = [self.attribute_secondary_dropdown, self.attribute_secondary_label]
        self.view_map_widgets = [self.county_btn, self.state_btn]

        # Initialize Stream widgets
        self.stream_dropdown, self.stream_label = self.initialize_stream_widgets()

        self.stream_widgets = [self.stream_dropdown, self.stream_label]

        # Initialize universal widgets
        title = QLabel('COVID-19 Vaccine Hesitancy Visualization')
        title.setFont(QFont('Times', 18))

        self.bubble_btn = QPushButton('Bubble Chart View', self)
        self.bubble_btn.clicked.connect(self.bubblechart_plot)

        self.map_btn = QPushButton('Map View', self)
        self.map_btn.clicked.connect(self.map_plot)

        self.stream_btn = QPushButton('Stream Graph View', self)
        self.stream_btn.clicked.connect(self.stream_plot)

        self.layout.addWidget(title, 0, 0, 1, 2)
        self.layout.addWidget(self.canvas, 1, 0, 1, 4)
        self.layout.addWidget(self.bubble_btn, 6, 0, 1, 2)
        self.layout.addWidget(self.map_btn, 6, 2, 1, 1)
        self.layout.addWidget(self.stream_btn, 6, 3, 1, 1)

        self.setLayout(self.layout)
        self.overview_data = self.date_data
        self.bubblechart_plot()

    def initialize_bubble_widgets(self):
        # Size Attribute
        size_dropdown = QComboBox(self)
        size_dropdown.activated[str].connect(self.set_size)
        size_dropdown.addItems(constants.SIZE_ATTRIBUTES)
        size_dropdown.setCurrentIndex(0)

        # Size Label
        size_label = QLabel('Size of Counties:')

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
        self.layout.addWidget(size_label, 4, 2, 1, 2)
        self.layout.addWidget(size_dropdown, 5, 2, 1, 2)
        self.layout.addWidget(svi_min_label, 2, 0, 1, 2)
        self.layout.addWidget(svi_min_slider, 3, 0, 1, 2)
        self.layout.addWidget(svi_max_label, 2, 2, 1, 2)
        self.layout.addWidget(svi_max_slider, 3, 2, 1, 2)
        self.layout.addWidget(population_label, 4, 0, 1, 2)
        self.layout.addWidget(population_slider, 5, 0, 1, 2)

        return size_dropdown, size_label, svi_min_slider, svi_min_label, \
               svi_max_slider, svi_max_label, population_slider, population_label

    def initialize_map_widgets(self):
        # Attribute Dropdown
        attribute_dropdown = QComboBox(self)
        attribute_dropdown.activated[str].connect(self.set_attribute)
        attribute_dropdown.addItems(list(constants.MAP_ATTRIBUTES.keys()))
        attribute_dropdown.setCurrentIndex(0)

        # Attribute Label
        attribute_label = QLabel('Attribute Encoded by Color:')

        # Date Dropdown
        date_dropdown = QComboBox(self)
        date_dropdown.activated[str].connect(self.set_date)
        date_dropdown.addItems(list(constants.REPORT_DATES))
        date_dropdown.setCurrentIndex(0)

        # Date Label
        date_label = QLabel('Report Date:')

        # State Dropdown
        state_dropdown = QComboBox(self)
        state_dropdown.activated[str].connect(self.set_state)
        state_dropdown.addItems(list(constants.US_STATES))
        state_dropdown.setCurrentIndex(0)

        # State Label
        state_label = QLabel('Select a state to view:')

        # Secondary Attribute Dropdown
        attribute_secondary_dropdown = QComboBox(self)
        attribute_secondary_dropdown.activated[str].connect(self.set_secondary)
        attribute_secondary_dropdown.addItems(list(constants.SECONDARY_MAP_ATTRIBUTES.keys()))
        attribute_secondary_dropdown.setCurrentIndex(0)

        # Secondary Attribute Label
        attribute_secondary_label = QLabel('Attribute Encoded by Size:')

        # Secondary default to hide
        attribute_secondary_dropdown.hide()
        attribute_secondary_label.hide()

        # County View Button
        county_btn = QPushButton('County by County', self)
        county_btn.clicked.connect(self.county_view)

        # State View Button
        state_btn = QPushButton('State by State', self)
        state_btn.clicked.connect(self.state_view)

        # Build Label
        self.layout.addWidget(attribute_label, 4, 2, 1, 2)
        self.layout.addWidget(attribute_dropdown, 5, 2, 1, 2)
        self.layout.addWidget(date_label, 2, 0, 1, 2)
        self.layout.addWidget(date_dropdown, 3, 0, 1, 2)
        self.layout.addWidget(state_label, 2, 2, 1, 2)
        self.layout.addWidget(state_dropdown, 3, 2, 1, 2)
        self.layout.addWidget(attribute_secondary_label, 4, 0, 1, 2)
        self.layout.addWidget(attribute_secondary_dropdown, 5, 0, 1, 2)
        self.layout.addWidget(county_btn, 4, 0, 1, 2)
        self.layout.addWidget(state_btn, 5, 0, 1, 2)

        return attribute_dropdown, attribute_label, date_dropdown, date_label, state_dropdown, \
               state_label, attribute_secondary_dropdown, attribute_secondary_label, county_btn, state_btn

    def initialize_stream_widgets(self):
        # Attribute Dropdown
        stream_dropdown = QComboBox(self)
        stream_dropdown.activated[str].connect(self.set_stream_attribute)
        stream_dropdown.addItems(list(constants.STREAM_ATTRIBUTES.keys()))
        stream_dropdown.setCurrentIndex(0)

        # Attribute Label
        stream_label = QLabel('Attribute Encoded by Color:')

        # Build Layout
        self.layout.addWidget(stream_label, 2, 0, 1, 4)
        self.layout.addWidget(stream_dropdown, 3, 0, 1, 4)

        return stream_dropdown, stream_label

    def county_view(self):
        self.view = 'County'
        self.map_plot()

    def state_view(self):
        self.view = 'State'
        self.map_plot()

    def set_size(self, text):
        self.size_attribute = text
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

    def set_date(self, text):
        self.overview_data = preprocessing.process_date(self.community_df, self.hesitancy_df, text)
        self.map_plot()

    def set_attribute(self, text):
        self.attribute_key = text
        self.map_plot()

    def set_state(self, text):
        self.state = text
        if self.state == 'Country View':
            self.secondary = 'None'
            self.secondary_map_widgets[0].setCurrentIndex(0)
        self.map_plot()

    def set_secondary(self, text):
        self.secondary = text
        self.map_plot()

    def set_stream_attribute(self, text):
        self.stream_attribute = text
        self.stream_plot()

    def bubblechart_plot(self):
        self.figure.clear()

        # BUBBLE WIDGETS: SHOW
        for widget in self.bubble_widgets:
            widget.show()

        # MAP WIDGETS: HIDE
        for widget in [*self.primary_map_widgets, *self.view_map_widgets,
                       *self.secondary_map_widgets]:
            widget.hide()

        # STREAM WIDGETS: HIDE
        for widget in self.stream_widgets:
            widget.hide()

        ax = self.figure.add_subplot(111)
        bubble_chart.plot(self.overview_data, ax, self.size_attribute,
                          self.svi_min_threshold, self.svi_max_threshold,
                          self.population_threshold)

        self.canvas.draw()

    def map_plot(self):
        self.figure.clear()

        # BUBBLE WIDGETS: HIDE
        for widget in self.bubble_widgets:
            widget.hide()

        # MAP WIDGETS: SHOW
        for widget in self.primary_map_widgets:
            widget.show()

        if self.state != 'Country View':
            self.secondary_map_widgets[0].show()
            self.secondary_map_widgets[1].show()
            self.view_map_widgets[0].hide()
            self.view_map_widgets[1].hide()
        else:
            self.secondary_map_widgets[0].hide()
            self.secondary_map_widgets[1].hide()
            self.view_map_widgets[0].show()
            self.view_map_widgets[1].show()

        # STREAM WIDGETS: HIDE
        for widget in self.stream_widgets:
            widget.hide()

        ax = self.figure.add_subplot(111)
        map.plot(self.overview_data, ax, self.state, self.attribute_key, self.secondary, self.view)

        self.canvas.draw()

    def stream_plot(self):
        self.figure.clear()

        # BUBBLE WIDGETS: HIDE
        for widget in self.bubble_widgets:
            widget.hide()

        # MAP WIDGETS: HIDE
        for widget in [*self.primary_map_widgets, *self.view_map_widgets,
                       *self.secondary_map_widgets]:
            widget.hide()

        # STREAM WIDGETS: SHOW
        for widget in self.stream_widgets:
            widget.show()

        ax = self.figure.add_subplot(111)
        stream_graph.plot(self.community_df, self.stream_attribute, ax)

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
