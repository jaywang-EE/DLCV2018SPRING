from params import *
import random
import numpy as np

import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.utils.data as Data

torch.manual_seed(326)
class E(nn.Module):
    def __init__(self):
        super(E, self).__init__()
        self.E1C = nn.Sequential(  #OP shape (3, 32, 32)
            nn.Conv2d(
                in_channels=3,     # input height
                out_channels=int(filters/8),    # n_filters
                kernel_size=4,     # filter size
                stride=2,          # filter movement/step
                padding=1,
            ),
            nn.LeakyReLU(0.2)
        ).double()
        self.E2C = nn.Sequential(  #OP shape (8, 16, 16)
            nn.Conv2d(int(filters/8),int(filters/4),4,2,1),
            nn.BatchNorm2d(int(filters/4)),
            nn.LeakyReLU(0.2)
#            nn.MaxPool2d(kernel_size=2)
        ).double()
        self.E3C = nn.Sequential( #OP shape (16, 8, 8)
            nn.Conv2d(int(filters/4),int(filters/2),4,2,1),
            nn.BatchNorm2d(int(filters/2)),
            nn.LeakyReLU(0.2)
#            nn.MaxPool2d(kernel_size=2)
        ).double()
        self.E4C = nn.Sequential( #OP shape (32, 4, 4)
            nn.Conv2d(int(filters/2),filters,4,2,1),
            nn.BatchNorm2d(filters),
            nn.LeakyReLU(0.2)
#            nn.MaxPool2d(kernel_size=2)
        ).double()
        #self.E5L = nn.Linear(int(COL/8*ROW/8*filters), ChannelEnc).double()
    def forward(self, x):
        x = x.permute([0,3,1,2])
        x = self.E1C(x)
        x = self.E2C(x)
        x = self.E3C(x)
        x = self.E4C(x)
        '''
        x = x.view(-1, int(COL/8*ROW/8*filters))
        x = self.E5L(x)
        '''
        return x

class D(nn.Module):
    def __init__(self):
        super(D, self).__init__()
        '''
        self.D1H = nn.Linear(ChannelEnc, ChannelEnc).double()
        self.D2H = nn.Linear(ChannelEnc, int(COL/8*ROW/8*filters)).double()
        '''
        self.D1U = nn.Sequential( #OP shape (32, 4, 4)
            nn.ConvTranspose2d(ChannelEnc, int(filters), 4, 1, 0),
            nn.BatchNorm2d(filters),
            nn.LeakyReLU(0.2)
        ).double()
        self.D2U = nn.Sequential( #OP shape (16, 8, 8)
            nn.ConvTranspose2d(filters, int(filters/2), 4, 2, 1),#2, stride=2),#
            nn.BatchNorm2d(int(filters/2)),
            nn.LeakyReLU(0.2)
        ).double()
        self.D3U = nn.Sequential( #OP shape (8, 16, 16)
            nn.ConvTranspose2d(int(filters/2), int(filters/4), 4, 2, 1),#2, stride=2),
            nn.BatchNorm2d(int(filters/4)),
            nn.LeakyReLU(0.2)
        ).double()
        self.D4U = nn.Sequential( #OP shape (4, 32, 32)
            nn.ConvTranspose2d(int(filters/4), int(filters/8), 4, 2, 1),#2, stride=2),#
            nn.BatchNorm2d(int(filters/8)),
            nn.LeakyReLU(0.2)
        ).double()
        self.D5U = nn.Sequential( #OP shape (3, 64, 64)
            nn.ConvTranspose2d(int(filters/8),3,4,2,1),
            nn.Tanh()
        ).double()
    def forward(self, x):
        x = self.D1U(x.view(-1, ChannelEnc, 1, 1))
        x = self.D2U(x)
        x = self.D3U(x)
        x = self.D4U(x)
        x = self.D5U(x)
        return x.permute([0,2,3,1])

class Generator(nn.Module):
    """docstring for Generator"""
    def __init__(self, decoder):
        super(Generator, self).__init__()
        self.decoder = decoder
    def forward(self, x):
        return self.decoder(x)

        
class Discreminator(nn.Module):
    """docstring for Discreminator"""
    def __init__(self, encoder):
        super(Discreminator, self).__init__()
        self.encoder = encoder
        '''
        self.Dis1L = nn.Linear(ChannelEnc, 128).double()
        self.Dis2L = nn.Linear(128, 32).double()
        '''
        self.Dis3L = nn.Sequential(
            nn.Conv2d(filters, 1, 4, 1, 0, bias=False),
            nn.Sigmoid()
        ).double()
    def forward(self, x):
        x = self.encoder(x)
        #x = self.Dis1L(x)
        #x = self.Dis2L(x)
        x = self.Dis3L(x)
        x = x.view(-1, 1)
        return x
class VAE(nn.Module):
    def __init__(self, encoder, decoder, Istest=False):
        super(VAE, self).__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.mean = nn.Linear(ChannelEnc, ChannelEnc).double()
        self.log_var = nn.Linear(ChannelEnc, ChannelEnc).double()
        self.Istest = Istest
    def _sampling(self, x_enc):
        self.z_mean = self.mean(x_enc)
        self.z_log_var = self.log_var(x_enc)
        std_z = torch.from_numpy(np.random.random(size=(self.z_mean.size()))).double()
        if Iscuda:
            epsilon = torch.cuda.DoubleTensor(1).uniform_()
        else:
            epsilon = torch.DoubleTensor(1).uniform_()
        if self.Istest:
            return self.z_mean
        else:
            return self.z_mean + torch.exp(self.z_log_var/2).mul(Variable(epsilon))

    def forward(self, x):
        x_enc = self.encoder(x)
        z = self._sampling(x_enc)
        return self.decoder(z)
'''
class E(nn.Module):
    def __init__(self):
        super(E, self).__init__()
        self.E1C = nn.Sequential(  #OP shape (3, 64, 64)
            nn.Conv2d(
                in_channels=3,     # input height
                out_channels=3,    # n_filters
                kernel_size=3,     # filter size
                stride=1,          # filter movement/step
                padding=1,
            ),
            nn.LeakyReLU(0.2)
        ).double()
        self.E11C = nn.Sequential(  #OP shape (32, 32, 32)
            nn.Conv2d(3,3,3,1,1),
            nn.LeakyReLU(0.2),
        ).double()
        self.E2C = nn.Sequential(  #OP shape (32, 32, 32)
            nn.Conv2d(3,filters,3,1,1),
            nn.LeakyReLU(0.2),
            nn.MaxPool2d(kernel_size=2)
        ).double()
        self.E3C = nn.Sequential( #OP shape (32, 16, 16)
            nn.Conv2d(filters,filters,3,1,1),
            nn.LeakyReLU(0.2),
            nn.MaxPool2d(kernel_size=2)
        ).double()
        self.E31C = nn.Sequential(  #OP shape (32, 32, 32)
            nn.Conv2d(filters,filters,3,1,1),
            nn.LeakyReLU(0.2),
        ).double()
        self.E4C = nn.Sequential( #OP shape (32, 8, 8)
            nn.Conv2d(filters,filters,3,1,1),
            nn.LeakyReLU(0.2),
            nn.MaxPool2d(kernel_size=2)
        ).double()

        self.E5L = nn.Linear(int(COL/8*ROW/8*filters), ChannelEnc).double()
    def forward(self, x):
        x = x.permute([0,3,1,2])
        x = self.E1C(x)
        x = self.E11C(x)
        x = self.E2C(x)
        x = self.E3C(x)
        x = self.E31C(x)
        x = self.E4C(x)
        x = x.view(-1, int(COL/8*ROW/8*filters))
        x = self.E5L(x)
        return x

class D(nn.Module):
    def __init__(self):
        super(D, self).__init__()
        self.D1H = nn.Linear(ChannelEnc, ChannelEnc).double()
        self.D2H = nn.Linear(ChannelEnc, int(COL/2*ROW/2*filters)).double()
        self.D3U = nn.Sequential( #OP shape (32, 32, 32)
            nn.UpsamplingNearest2d(scale_factor=2),
            nn.Conv2d(filters,filters,3,2,1),
            nn.LeakyReLU(0.2)
        ).double()
        self.D4U = nn.Sequential( #OP shape (32, 32, 32)
            nn.Conv2d(filters,filters,3,1,1),
            nn.UpsamplingNearest2d(scale_factor=2),
            nn.LeakyReLU(0.2)
        ).double()
        self.D41U = nn.Sequential( #OP shape (32, 32, 32)
            nn.Conv2d(filters,filters,3,1,1),
            nn.LeakyReLU(0.2)
        ).double()
        self.D5U = nn.Sequential( #OP shape (32, 32, 32)
            nn.Conv2d(filters,filters,3,1,1),
            nn.UpsamplingNearest2d(scale_factor=2),
            nn.LeakyReLU(0.2)
        ).double()
        self.D51U = nn.Sequential( #OP shape (32, 32, 32)
            nn.Conv2d(filters,filters,3,1,1),
            nn.LeakyReLU(0.2)
        ).double()
        self.D6C = nn.Sequential( #OP shape (32, 32, 32)
            nn.Conv2d(filters,3,3,2,1),
            nn.LeakyReLU(0.2)
        ).double()
    def forward(self, x):
        x = self.D1H(x)
        x = self.D2H(x)
        x = x.view(-1, int(COL/2), int(ROW/2), filters)
        x = self.D3U(x)
        x = self.D4U(x)
        x = self.D41U(x)
        x = self.D5U(x)
        x = self.D51U(x)
        x = self.D6C(x)
        return x.permute([0,2,3,1])

'''