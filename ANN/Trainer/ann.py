#! /usr/bin/python

from input_layer  import InputLayer
from hidden_layer import HiddenLayer
from output_layer import OutputLayer

import polls.models as models


class ANN:
	def __init__(self, userid):
		self.inputLayer  = InputLayer()
		self.hiddenLayers = []
		self.outputLayer = OutputLayer()

		self.userid = userid
		self.outputs = []

	def init(self, layers_data):
		self.layers_data = layers_data
		for i in range(1, len(layers_data) - 1):
			self.hiddenLayers.append(HiddenLayer())
			self.hiddenLayers[-1].init(layers_data[i - 1] + 1, layers_data[i])

		self.outputLayer.init(layers_data[-2] + 1, layers_data[-1])

		"""self.hiddenLayers[0].neurons[0].weights = [0.5, 0.4, -0.8]
		self.hiddenLayers[0].neurons[1].weights = [0.9, 1.0, 0.1]
		self.outputLayer.neurons[0].weights = [-1.2, 1.1, -0.3]"""

		self.outputs = [0 for i in range(layers_data[-1])]

	def activate(self, input_data):
		self.inputLayer.init(input_data)

		self.hiddenLayers[0].activate(self.inputLayer.data)
		for i in range(1, len(self.hiddenLayers)):
			self.hiddenLayers[i].activate(self.hiddenLayers[i - 1].outputs)

		self.outputLayer.activate(self.hiddenLayers[-1].outputs)

		self.outputs = self.outputLayer.outputs

	def updateErrorGradients(self, desiredOutputs):
		sum_errors = self.outputLayer.updateErrorGradients(desiredOutputs)

		self.hiddenLayers[-1].updateErrorGradients(self.outputLayer)
		for i in range(len(self.hiddenLayers) - 2, -1, -1):
			self.hiddenLayers[i].updateErrorGradients(self.hiddenLayers[i + 1])

		return sum_errors

	def updateWeights(self, learningRate):
		self.hiddenLayers[0].updateWeights(self.inputLayer.data, learningRate)
		for i in range(1, len(self.hiddenLayers)):
			self.hiddenLayers[i].updateWeights(self.hiddenLayers[i - 1].outputs, learningRate)

		self.outputLayer.updateWeights(self.hiddenLayers[-1].outputs, learningRate)

	def saveData(self):
		data = []
		data.append(self.layers_data)
		for h in self.hiddenLayers:
			for n in h.neurons:
				data.append(n.weights)

		for n in self.outputLayer.neurons:
			data.append(n.weights)

		if not models.Ann_net_data.objects.filter(userid=self.userid):
			models.Ann_net_data.objects.create(userid=self.userid, data=str(data))
		else:
			models.Ann_net_data.objects.filter(userid=self.userid).update(data=str(data))

		del data

	def loadData(self):
		if not models.Ann_net_data.objects.filter(userid=self.userid):
			return

		data = eval(models.Ann_net_data.objects.get(userid=self.userid).data)

		self.init(data[0])

		index = 1
		for h in self.hiddenLayers:
			for n in h.neurons:
				n.weights = data[index]
				index += 1

		for n in self.outputLayer.neurons:
			n.weights = data[index]
			index += 1

		del data
		return True


	def __str__(self):
		result = ""

		result += "----------------->input layer :\n"  + str(self.inputLayer) + '\n'
		for h in self.hiddenLayers:
			result += "----------------->hidden layer :\n" + str(h) + '\n'
		result += "----------------->output layer :\n" + str(self.outputLayer) + '\n'

		result += "----------------->outputs :\n" + str(self.outputs)

		return result

