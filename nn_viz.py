from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen
import sys
from typing import List
from neural_network import *
from mario import Mario

class NeuralNetworkViz(QtWidgets.QWidget):
    def __init__(self, parent, mario: Mario, size):
        super().__init__(parent)
        self.mario = mario
        self.size = size
        self.horizontal_distance_between_layers = 50
        self.vertical_distance_between_nodes = 10
        # self.num_neurons_in_largest_layer = max(self.mario.network.layer_nodes)
        l=[25, 12, 9, 6]
        self.num_neurons_in_largest_layer = max(l[1:])
        # self.setFixedSize(600,800)
        self.neuron_locations = {}
        # Set all neuron locations for layer 0 (Input) to be at the same point.
        # The reason I do this is because the number of inputs can easily become too many to show on the screen.
        # For this reason it is easier to not explicitly show the input nodes and rather show the bounding box of the rectangle.
        #@TODO: Make the values of 150, 5, 16, 15 come from the parent
        self.x_offset = 150 + 16//2*16 + 5
        self.y_offset = 5 + 15*16 + 5
        for nid in range(l[0]):
            t = (0, nid)
            
            self.neuron_locations[t] = (self.x_offset, self.y_offset)
        self.show()


    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter()
        painter.begin(self)

        self.show_network(painter)
        
        painter.end()

    def update(self) -> None:
        self.repaint()

    def show_network(self, painter: QtGui.QPainter):
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        painter.setRenderHints(QtGui.QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        painter.setPen(QPen(Qt.black, 1.0, Qt.SolidLine))
        horizontal_space = 20  # Space between Nodes within the same layer
        radius = 8
        height = self.frameGeometry().height()
        width = self.frameGeometry().width()
        layer_nodes = self.mario.network.layer_nodes

        default_offset = self.x_offset
        h_offset = self.x_offset
        v_offset = self.y_offset + 50
        inputs = self.mario.inputs_as_array
        out = self.mario.network.feed_forward(inputs)  # @TODO: shouldnt need this

        active_outputs = np.where(out > 0.5)[0]
        max_n = self.size[0] // (2* radius + horizontal_space)
        
        # Draw nodes
        for layer, num_nodes in enumerate(layer_nodes[1:], 1):
            h_offset = (((max_n - num_nodes)) * (2*radius + horizontal_space))/2
            activations = None
            if layer > 0:
                activations = self.mario.network.params['A' + str(layer)]

            for node in range(num_nodes):
                x_loc = node * (radius*2 + horizontal_space) + h_offset
                y_loc = v_offset
                t = (layer, node)
                if t not in self.neuron_locations:
                    self.neuron_locations[t] = (x_loc + radius, y_loc)
                
                painter.setBrush(QtGui.QBrush(Qt.white, Qt.NoBrush))
                # Input layer
                if layer == 0:
                    # Is there a value being fed in
                    if inputs[node, 0] > 0:
                        painter.setBrush(QtGui.QBrush(Qt.green))
                    else:
                        painter.setBrush(QtGui.QBrush(Qt.white))
                # Hidden layers
                elif layer > 0 and layer < len(layer_nodes) - 1:
                    try:
                        saturation = max(min(activations[node, 0], 1.0), 0.0)
                    except:
                        print(self.mario.network.params)
                        import sys
                        sys.exit(-1)
                    painter.setBrush(QtGui.QBrush(QtGui.QColor.fromHslF(125/239, saturation, 120/240)))
                # Output layer
                elif layer == len(layer_nodes) - 1:
                    text = ('U', 'D', 'L', 'R', 'A', 'B')[node]
                    painter.drawText(h_offset + node * (radius*2 + horizontal_space), v_offset + 2*radius + 2*radius, text)
                    if node in active_outputs:
                        painter.setBrush(QtGui.QBrush(Qt.green))
                    else:
                        painter.setBrush(QtGui.QBrush(Qt.white))

                painter.drawEllipse(x_loc, y_loc, radius*2, radius*2)
            v_offset += 150

        # Reset horizontal offset for the weights
        h_offset = default_offset

        # Draw weights
        # For each layer starting at 1
        for l in range(1, len(layer_nodes)):
            weights = self.mario.network.params['W' + str(l)]
            prev_nodes = weights.shape[1]
            curr_nodes = weights.shape[0]
            # For each node from the previous layer
            for prev_node in range(prev_nodes):
                # For all current nodes, check to see what the weights are
                for curr_node in range(curr_nodes):
                    # If there is a positive weight, make the line blue
                    if weights[curr_node, prev_node] > 0:
                        painter.setPen(QtGui.QPen(Qt.blue))
                    # If there is a negative (impeding) weight, make the line red
                    else:
                        painter.setPen(QtGui.QPen(Qt.red))
                    # Grab locations of the nodes
                    start = self.neuron_locations[(l-1, prev_node)]
                    end = self.neuron_locations[(l, curr_node)]
                    # Offset start[0] by diameter of circle so that the line starts on the right of the circle
                    painter.drawLine(start[0], start[1] + radius*2, end[0], end[1])