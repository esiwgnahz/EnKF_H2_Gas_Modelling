#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'zq'

import numpy as np
import pandas as pd

class read_write_values:
    '''
    Nod_num is the number of nodes
    the shape of para is Nod_num*1, and the p1 & p2 are the same
    '''
    def __init__(self,obs_Num,para,p1,p2,i,Nod_num=451):
        self.Nod_num=Nod_num
        self.obs_Num=obs_Num
        self.para=para
        self.p1=p1
        self.p2=p2
        self.i=i

    #定义函数，读取输出的每个点的压力头值
    def read_p(self):
        result=r'E:\ENKF_LabGasInjec2\gas_%d\H2_Permeability_GasPressure_domain_quad.tec' % self.i
        f=open(result,'r')
        Nod_inf=f.readlines()
        last=Nod_inf[-(400+self.Nod_num):-400]
        f.close()
        head=[None]*self.Nod_num
        for m in xrange(len(last)):
            line=last[m].split()
            head[m]=line[3:5]

        head=np.array(head)
        head=np.float64(head)
        pressure1=np.zeros([self.Nod_num])
        pressure2=np.zeros([self.Nod_num])
        for n in range(len(head)):
            pressure1[n]=head[n,0]
            pressure2[n]=head[n,1]
        return pressure1,pressure2

    #定义函数，读取观测点处对应的预测值
    def read_obs(self):
        args_obs=r'E:\ENKF_LabGasInjec2\gas_%d\H2_Permeability_GasPressure_domain_quad.tec' %self.i
        f=open(args_obs,'r')
        Nod_inf=f.readlines()
        last=Nod_inf[-(400+self.Nod_num):-400]
        f.close()
        for m in xrange(self.Nod_num):
            last[m]=last[m].split()
        last=pd.DataFrame(last)
        obs_prediction=last.ix[self.obs_Num,[3,4]]
        obs_prediction=obs_prediction.values
        obs_prediction=np.float64(obs_prediction)
        obs_p1=obs_prediction[:,0]
        obs_p2=obs_prediction[:,1]
        return obs_p1,obs_p2


    #定义函数，将参数写入ki.direct
    def write_ki(self):
        Ki=self.para
        args_ki=r'E:\ENKF_LabGasInjec2\gas_%d\H2_Permeability_GasPressure_KI.direct' %self.i
        with open(args_ki,'r') as f:
            content=f.readlines()
        content1=content[:-1]
        for m in xrange(len(content1)):
            content[m]=''
            line=content1[m].split()
            line[1]=str(Ki[m])
            for ii in range(len(line)):
                content[m]+=line[ii]+' '
            content[m]+='\n'
            with open(args_ki,'w') as f:
                for line in content:
                    f.write(line)
                    pass



    # 定义函数，将更新之后的p1,p2的值写入direct文件
    def write_p1(self):
        P1=self.p1
        args_p1=r'E:\ENKF_LabGasInjec2\gas_%d\H2_Permeability_GasPressure_PRESSURE1.direct' % self.i
        with open(args_p1,'r') as f:
            content=f.readlines()
        content1=content[:-1]
        for m in xrange(len(content1)):
            content[m]=''
            line=content1[m].split()
            line[1]=str(P1[m])
            for ii in range(len(line)):
                content[m]+=line[ii]+' '
            content[m]+='\n'
            with open(args_p1,'w') as f:
                for line in content:
                    f.write(line)
                    pass


    def write_p2(self):
        P2=self.p2
        args_p2=r'E:\ENKF_LabGasInjec2\gas_%d\H2_Permeability_GasPressure_PRESSURE2.direct' % self.i
        with open(args_p2,'r') as f:
            content=f.readlines()
        content1=content[:-1]
        for i in xrange(len(content1)):
            content[i]=''
            line=content1[i].split()
            line[1]=str(P2[i])
            for ii in range(len(line)):
                content[i]+=line[ii]+' '
            content[i]+='\n'
            with open(args_p2,'w') as f:
                for line in content:
                    f.write(line)
                    pass

