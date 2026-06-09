# Practice to gain understanding of Neural Network
# Doesn't really work but it helped me understand the theory :)
import numpy as np

possibleInputs = [[0, 0], [0, 1], [1, 0], [1, 1]]

def sigmoid(z):
    return(1 / (1 + np.exp(-z)))

class NodeData:
    def __init__(self, w1, w2):
        self.weight = [w1, w2]
        self.bias = 0

learnrate = 0.5

N1 = NodeData(0.3, -0.9)
N2 = NodeData(-0.4, 0.2)
output = NodeData(0.6, -0.1)

for i in range(10000):
    for [input1, input2] in possibleInputs:
        target = input1 ^ input2

        # Activation functions
        L1output = [sigmoid(input1 * N1.weight[0] + input2 * N1.weight[1] + N1.bias), sigmoid(input1 * N2.weight[0] + input2 * N2.weight[1] + N2.bias)]
        L2output = sigmoid(L1output[0] * output.weight[0] + L1output[1] * output.weight[1] + output.bias)

        # Error
        error = target - L2output
        grad = error * L2output * (1 - L2output)
        L1error = [grad * output.weight[0], grad * output.weight[1]]
        L1grad = [L1output[0] * (1 - L1output[0]) * L1error[0], L1output[1] * (1 - L1output[1]) * L1error[1]]

        # Iterations
        N1.weight[0] += learnrate * L1grad[0] * input1
        N1.weight[1] += learnrate * L1grad[0] * input2
        N2.weight[0] += learnrate * L1grad[1] * input1
        N2.weight[1] += learnrate * L1grad[1] * input2
        output.weight[0] += L1output[0] * grad * learnrate
        output.weight[1] += L1output[1] * grad * learnrate

        N1.bias += L1grad[0] * learnrate
        N2.bias += L1grad[1] * learnrate
        output.bias += grad * learnrate

print("Training complete!")

input1 = int(input("Input 1 (0 or 1): "))
input2 = int(input("Input 2 (0 or 1): "))
target = input1 ^ input2

L1output = [
    sigmoid(input1 * N1.weight[0] + input2 * N1.weight[1] + N1.bias), 
    sigmoid(input1 * N2.weight[0] + input2 * N2.weight[1] + N2.bias)
]
prediction = L1output[0] * output.weight[0] + L1output[1] * output.weight[1] + output.bias

print(f"Target: {target:>2} | Prediction: {prediction:.4f}")