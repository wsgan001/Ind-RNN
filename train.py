import torch as th
import torchvision
from torch.autograd import Variable
from torch import nn
from torch import optim
from torchvision import datasets
import torchvision.transforms as transforms
from sequential_mnist import loadSequentialMNIST
from IndRNN import IndRNNModel
from RNNs import LSTMModel, GRUModel, RNNModel
    #IndRNNModel


def train(model, batchSize, epoch, useCuda = False):

    if useCuda:
        model = model.cuda()

    checkPoint = 10

    optimizer = optim.Adam(model.parameters(), lr=0.01, )
    ceriation = nn.NLLLoss()
    trainLoader, testLoader = loadSequentialMNIST(batchSize=batchSize)

    for i in range(epoch):

        # trainning
        sum_loss = 0

        for batch_idx, (x, target) in enumerate(trainLoader):
            optimizer.zero_grad()
            if useCuda:
                x, target = x.cuda(), target.cuda()
            x, target = Variable(x), Variable(target)
            out = model(x, batchSize)

            loss = ceriation(out, target)
            #print("batch loss:", loss.data[0])
            sum_loss += loss.data[0]
            loss.backward()
            optimizer.step()

            if (batch_idx + 1) % checkPoint == 0 or (batch_idx + 1) == len(trainLoader):
                print('==>>> epoch: {}, batch index: {}, train loss: {:.6f}'.format( i, batch_idx + 1, sum_loss/checkPoint))
                sum_loss = 0.0

        # testing
        correct_cnt, sum_loss = 0, 0
        total_cnt = 0
        for batch_idx, (x, target) in enumerate(testLoader):

            x, target = Variable(x, volatile=True), Variable(target, volatile=True)
            if useCuda:
                x, target = x.cuda(), target.cuda()
            out = model(x, batchSize)
            loss = ceriation(out, target)
            _, pred_label = th.max(out.data, 1)
            total_cnt += x.data.size()[0]
            correct_cnt += (pred_label == target.data).sum()

            if (batch_idx + 1) % 100 == 0 or (batch_idx + 1) == len(testLoader):
                print('==>>> epoch: {}, batch index: {}, test loss: {:.6f}, acc: {:.3f}'.format(
                    i, batch_idx + 1, sum_loss/batch_idx, correct_cnt * 1.0 / total_cnt))


if __name__ == '__main__':

    epoch = 10
    batchSize = 128
    model = IndRNNModel(inputDim=28, hiddenNum=256, outputDim=10, layerNum=3)
    # model = RNNModel(inputDim=28, hiddenNum=256, outputDim=10, layerNum=1)
    # model = GRUModel(inputDim=28, hiddenNum=256, outputDim=10, layerNum=1)
    # model = LSTMModel(inputDim=28, hiddenNum=256, outputDim=10, layerNum=1)
    train(model, batchSize, epoch, useCuda=True)