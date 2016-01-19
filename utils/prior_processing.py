#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'zq'

import numpy as np
import math
import os
import shutil
import pandas as pd

class initialization:
    def __init__(self,sigma,deltax,deltay,x,y,dx,dy,Nod_num,ki_mean,N):
        self.sigma=sigma
        self.deltax=deltax
        self.deltay=deltay
        self.dx=dx
        self.dy=dy
        self.m=int(y/dy+1)
        self.n=int(x/dx+1)
        self.Nod_num=Nod_num
        self.ki_mean=ki_mean
        self.N=N

    def para_true(self):  #产生真实参数
        L1=self.generateL()
        ran=np.random.normal(0,1,size=self.Nod_num)
        ran=ran.reshape(self.Nod_num,1)
        lnpara=np.dot(L1,ran)
        mean=np.log(self.ki_mean)
        lnpara=lnpara+mean
        para=np.array(lnpara)
        para_true=para[:,-1]
        np.savetxt(r'E:\ENKF_LabGasInjec2\true_obs\para_true.txt',para_true)

    def para_init(self):   #产生初始参数样本
        L1=self.generateL()
        ran=np.random.normal(0,1,size=self.Nod_num)
        ran=ran.reshape(self.Nod_num,1)
        lnpara=np.dot(L1,ran)
        mean=np.log(self.ki_mean)
        lnpara=lnpara+mean
        para=[None]*self.Nod_num
        for i in xrange(self.Nod_num):
            para[i]=np.random.normal(lnpara[i],0.5,size=self.N)
        para=np.array(para)
        return para

    def p1_p2_init(self):    #获得初始p1,p2
        arg_p1_init=r'E:\ENKF_LabGasInjec2\PRESSURE1.direct'
        arg_p2_init=r'E:\ENKF_LabGasInjec2\PRESSURE2.direct'
        with open(arg_p1_init,'r') as f:
            content1=f.readlines()
        for i in range(len(content1)):
            content1[i]=content1[i].split()
        content1=pd.DataFrame(content1)
        content1=content1.values
        p1=content1[:-1,1]
        p1=np.float64(p1)

        with open(arg_p2_init,'r') as f:
            content2=f.readlines()
        for i in range(len(content2)):
            content2[i]=content2[i].split()
        content2=pd.DataFrame(content2)
        content2=content2.values
        p2=content2[:-1,1]
        p2=np.float64(p2)
        return p1,p2



    ##从domain中修改得到符合绘制参数分布图的tec文件
    def generate_para_distribution_tec(self):
        with open(r'E:\ENKF_LabGasInjec2\true_obs\H2_Permeability_GasPressure_domain_quad.tec','r') as f:
            content=f.readlines()
            content1=content[:3]
            content1[0]='VARIABLES  = "X","Y","Z", "Initial_Permeability" \n'
            content2=content[3:854]
            for i in range(len(content2)):
                line=content2[i].split()
                line[4:]=''
                content2[i]=' '.join(line[i] for i in range(len(line)))+'\n'

        content_modify=content1+content2
        with open(r'E:\ENKF_LabGasInjec2\true_obs\Ki_distribution_map.tec','w') as f:
            for line in content_modify:
                f.write(line)

        with open(r'E:\ENKF_LabGasInjec2\true_obs\para_true.txt','r') as f:
            para_true=f.readlines()
            for i in range(len(para_true)):
                line=para_true[i].split()
                para_true[i]=line[0]

        with open(r'E:\ENKF_LabGasInjec2\true_obs\Ki_distribution_map.tec','r') as f:
            content=f.readlines()
            content1=content[3:self.Nod_num+3]
            for i in range(len(content1)):
                line=content1[i].split()
                line[3]=para_true[i]
                content[i+3]=' '.join(line[i] for i in range(len(line)))+'\n'

        with open(r'E:\ENKF_LabGasInjec2\true_obs\Ki_distribution_map.tec','w') as f:
            for line in content:
                f.write(line)

    
	#产生供并发运算的文件
    def remove_generate_files(self):
        for i in xrange(self.N):
            file_args=r'E:\ENKF_LabGasInjec2\gas_{0}'.format(i)
            old=r'E:\ENKF_LabGasInjec2\gas_00'
            if os.path.exists(file_args):
                shutil.rmtree(file_args)
                shutil.copytree(old,file_args)
            else:
                shutil.copytree(old,file_args)

    def generateL(self):
        mn=self.m*self.n
        c=np.zeros((mn,mn))
        for i in xrange(mn):
            for j in xrange(mn):
                xi=int(math.floor(i/self.m))+1
                yi=i-self.m*(xi-1)
                xj=int(math.floor(j/self.m))+1
                yj=j-self.m*(xj-1)
                if yi==0:
                    xi=int(math.floor(i/self.m))
                    yi=self.m
                if yj==0:
                    xj=int(math.floor(j/self.m))
                    yj=self.m
                c[i,j]=math.pow(self.sigma,2)*(math.exp(-math.fabs((xi-xj)*self.dx)/self.deltax-math.fabs((yi-yj)*self.dy)/self.deltay))

        L=np.linalg.cholesky(c)
        return L





if __name__=='__main__':
	time_step=30
	Nod_num=451
	N=50
	varR=100
	obs_Num=[172,180,254,262,336,344]
	obs_num=len(obs_Num)
	sigma=0.6
	ki_mean=1e-18
	deltax=0.04
	deltay=0.1
	dx=0.005
	dy=0.005
	x=0.05
	y=0.2
	m=int(y/dy+1)
	n=int(x/dx+1)
    prior=initialization(sigma,deltax,deltay,x,y,dx,dy,Nod_num,ki_mean,N)
    # prior.generate_para_distribution_tec()
    prior.remove_generate_files()