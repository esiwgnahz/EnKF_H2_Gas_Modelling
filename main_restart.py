#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'zq'

import math
from math import e
import numpy as np
import pandas as pd
import win32api
import time
from gevent import pool
from utils.generate_obs import generate_obs
from utils.values_init import p1_p2_init,para_init
from utils.read_values import read_obs,read_p
from utils.write_values import write_ki,write_p1,write_p2
from utils.time_modify import time_modify

from utils.initialization import initialization
from utils.read_write_values import read_write_values

# varR=[100,100,100,100,100,100,1000,100,100,100,100,100,100,100,100,1000,100,100]
# varR=np.array(varR)
# varR=varR.reshape(-1,1)
# varR=varR.repeat(18,axis=1)
time_step=30
Nod_num=451
N=50
varR=100
obs_Num=[172,180,254,262,336,344]
obs_num=len(obs_Num)
ki_mean=1e-18
sigma=0.6
deltax=0.04
deltay=0.1
dx=0.005
dy=0.005
x=0.05
y=0.2
m=int(y/dy+1)
n=int(x/dx+1)



obs_Pressure1,obs_Pressure2=generate_obs(time_step,obs_num,varR,N)
t=1
y_p1=obs_Pressure1[t]
y_obs_p1=pd.DataFrame(y_p1)
y_obs_p1=y_obs_p1.T
y_obs_p1=y_obs_p1.values
y_p2=obs_Pressure2[t]
y_obs_p2=pd.DataFrame(y_p2)
y_obs_p2=y_obs_p2.T
y_obs_p2=y_obs_p2.values
y_obs=np.vstack((y_obs_p1,y_obs_p2))
np.savetxt('y_obs.txt',y_obs)

p_after=np.zeros([Nod_num*2,N])
y_obs_prediction=np.zeros([obs_num*2,N])

init=initialization(sigma,deltax,deltay,x,y,dx,dy,Nod_num,ki_mean,N)
p1_init,p2_init=init.p1_p2_init()  #获得水头的初始分布
p1_init=np.array(p1_init)
p1_init=p1_init.reshape(-1,1)
p1_init=p1_init.repeat(N,axis=1)
p2_init=np.array(p2_init)
p2_init=p2_init.reshape(-1,1)
p2_init=p2_init.repeat(N,axis=1)

para=init.para_init()
np.savetxt('ki_init.txt',para)
ki_ini=np.exp(para)

def runexe(ki_ini,pi_init,p2_init,i):
    args_exe=r'E:\ENKF_LabGasInjec2\gas_%d\ogs.exe' %i
    args=r'E:\ENKF_LabGasInjec2\gas_%d' % i
    values_manipulation=read_write_values(obs_Num,ki_ini[:,i],p1_init[:,i],p2_init[:,i],i)
    values_manipulation.write_ki()  #para为初始参数，样本之间存在随机扰动
    values_manipulation.write_p1()
    values_manipulation.write_p2()
    win32api.ShellExecute(0,'open',args_exe,'H2_Permeability_GasPressure',args,0)
    time.sleep(3)
    Obs_p1,Obs_p2=values_manipulation.read_obs()
    for ii in range(obs_num):
        y_obs_prediction[ii][i]=Obs_p1[ii]  #组成观测点处的预测值矩阵
    for mm in range(obs_num,obs_num*2):
        y_obs_prediction[mm][i]=Obs_p2[mm-obs_num]
    p1_predict,p2_predict=values_manipulation.read_p()
    for jj in range(Nod_num):
        p_after[jj][i]=p1_predict[jj]     #组成状态变量预测值矩阵
    for kk in range(Nod_num,Nod_num*2):
        p_after[kk][i]=p2_predict[kk-Nod_num]


taskpool=pool.Pool(4)
for i in range(N):
    taskpool.spawn(runexe,ki_ini,p1_init,p2_init,i)
    print i
taskpool.join()
print time.ctime()


np.savetxt('y_obs_prediction.txt',y_obs_prediction)
np.savetxt('p_after.txt',p_after)
x=np.vstack((para,p_after))
np.savetxt('x.txt',x)
x_average=np.average(x,axis=1)
y_obs_pre_ava=np.average(y_obs_prediction,axis=1)
np.savetxt('y_obs_pre_ave.txt',y_obs_pre_ava)
x_error=np.zeros([Nod_num*3,N])
y_error=np.zeros([obs_num*2,N])
for i in range(N):
    x_error[:,i]=x[:,i]-x_average[:]
    y_error[:,i]=y_obs_prediction[:,i]-y_obs_pre_ava[:]


np.savetxt('x_error.txt',x_error)
np.savetxt('y_error.txt',y_error)
ph=np.dot(x_error,y_error.T)/(N-1)
ph=np.matrix(ph)
hph=np.dot(y_error,y_error.T)/(N-1)
hph=np.matrix(hph+varR)
hph_var=hph.I
k=np.dot(ph,hph_var)
k=np.array(k)
np.savetxt('k.txt',k)
yy=np.zeros([obs_num*2,N])
for i in range(N):
    yy[:,i]=y_obs[:,i]-y_obs_prediction[:,i]
    x[:,i]=x[:,i]+np.dot(k,(y_obs[:,i]-y_obs_prediction[:,i]))

xx=x[0:Nod_num,:]    #需要大致检查x的每个元素，参数部分必须是负值，应该是ln(1e-18)左右的值，如果出现了正值，立马结束程序，另外状态变量出现了负值也立马结束程序
p1_1=x[Nod_num:Nod_num*2,:]
p1_2=x[Nod_num*2:,:]
np.savetxt('t_1.txt',xx)
np.savetxt('yy.txt',yy)
np.savetxt('x_1.txt',x)
if np.any(xx>0):
    print 'there is positive parameter'
    exit()
if np.any(p1_1<0):
    print 'there is negative p1'
    exit()
if np.any(p1_2<0):
    print 'there is negative p2'
    exit()

parY=np.zeros((Nod_num,time_step))
parY[:,0]=np.average(x[0:Nod_num,:],axis=1)
np.savetxt('parY_1.txt',parY[:,0])
df=pd.DataFrame(parY[:,0])
stat=df.describe()
std=stat.ix['std',[0]]
try:
    cov_init=np.sqrt(np.power(e,np.power(sigma,2))-1)
    cov=np.sqrt(np.power(e,np.power(std,2))-1)
    print 'initial covariance:',cov_init
    print 'std-1',std
    print 'cov_1',cov
except OverflowError:
    print 'cov is too large'

print time.ctime()


for t in range(2,5):
    try:
        KI=x[0:Nod_num,:]   #取出状态向量中的参数，将其进行指数恢复
        KI=np.exp(KI)
        for i in xrange(N):
            time_modify(t,i)

        taskpool3=pool.Pool(20)
        for i in range(N):
            taskpool3.spawn(runexe,KI,p1_init,p2_init,i)
            print i,'12'
        taskpool3.join()

        np.savetxt('p_after_%d.txt'%t,p_after)
        np.savetxt('y_obs_prediction_%d.txt'%t,y_obs_prediction)
        x=np.vstack((para,p_after))
        x_average=np.average(x,axis=1)
        y_obs_pre_ava=np.average(y_obs_prediction,axis=1)
        x_error=np.zeros([Nod_num*3,N])
        y_error=np.zeros([obs_num*2,N])

        y_p1=obs_Pressure1[t]
        y_obs_p1=pd.DataFrame(y_p1)
        y_obs_p1=y_obs_p1.T
        y_obs_p1=y_obs_p1.values
        y_p2=obs_Pressure2[t]
        y_obs_p2=pd.DataFrame(y_p2)
        y_obs_p2=y_obs_p2.T
        y_obs_p2=y_obs_p2.values
        y_obs=np.vstack((y_obs_p1,y_obs_p2))
        np.savetxt('y_obs_%d.txt' %t,y_obs)
        for i in range(N):
            x_error[:,i]=x[:,i]-x_average[:]
            y_error[:,i]=y_obs_prediction[:,i]-y_obs_pre_ava[:]

        ph=np.dot(x_error,y_error.T)/(N-1)
        ph=np.matrix(ph)
        hph=np.dot(y_error,y_error.T)/(N-1)
        hph=np.matrix(hph+varR)
        hph_var=hph.I
        k=np.dot(ph,hph_var)
        k=np.array(k)
        np.savetxt('k_%d.txt' %t,k)
        yy=np.zeros([obs_num*2,N])
        for i in range(N):
            yy[:,i]=y_obs[:,i]-y_obs_prediction[:,i]
            x[:,i]=x[:,i]+np.dot(k,(y_obs[:,i]-y_obs_prediction[:,i]))
        xx=x[0:Nod_num,:]
        p1_1=x[Nod_num:Nod_num*2,:]
        p1_2=x[Nod_num*2:,:]
        if np.any(xx>0):
             exit()
        if np.any(p1_1<0):
             exit()
        if np.any(p1_2<0):
             exit()
        np.savetxt('t_%d.txt' %t,xx)
        np.savetxt('x_%d.txt'%t,x)
        np.savetxt('yy_%d.txt' %t,yy)
        parY[:,t-1]=np.average(x[0:Nod_num,:],axis=1)
        np.savetxt('parY.txt',parY)
        df=pd.DataFrame(parY[:,t-1])
        stat=df.describe()
        std=stat.ix['std',[0]]
        try:
            cov=math.sqrt(math.pow(e,math.pow(std,2))-1)
            print 't_%d_std:'%t,std
            print 't_%d_cov:'%t,cov
        except OverflowError:
            print 'cov is too large'
        pass
    except Exception,e:
        print e
    # command='taskkill /F /IM ogs.exe'
    # os.system(command)

