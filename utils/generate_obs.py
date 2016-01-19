#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'zq'

import numpy as np
import pandas as pd
import win32api
import time
time_step=30
varR=100
args_exe=r'E:\ENKF_LabGasInjec2\true_obs\ogs.exe'
args=r'E:\ENKF_LabGasInjec2\true_obs'

obs_Num=[172,180,254,262,336,344]

###将之前生成的真实参数读取出来，并写入ki.direct

def read_write_Ki():
    args_para_true=r'E:\ENKF_LabGasInjec2\true_obs\para_true.txt'
    with open(args_para_true,'r') as f:
        content=f.readlines()
    for i in range(len(content)):
        content[i]=content[i].split()
    content=np.array(content)
    truepara=np.float64(content[:,0])
    Ki=np.exp(truepara)

    args_ki=r'E:\ENKF_LabGasInjec2\true_obs\H2_Permeability_GasPressure_KI.direct'
    with open(args_ki,'r') as f:
        content=f.readlines()
    content1=content[:-1]
    for i in range(len(content1)):
        content[i]=''
        line=content1[i].split()
        line[1]=str(Ki[i])
        for ii in range(len(line)):
            content[i]+=line[ii]+' '
        content[i]+='\n'
        with open(args_ki,'w') as f:
            for line in content:
                f.write(line)


##提取所有时间步的观测点处的预测值，加噪声之后作为观测值
def read_trueobs(t,obs_Num):
    args=r'E:\ENKF_LabGasInjec2\true_obs\H2_Permeability_GasPressure_domain_quad.tec'
    f=open(args,'r')
    content=f.readlines()
    x=np.empty((1,5))   #准备提取tec文件中每个时间步输出的前5列数据（x,y,z,p1,p2）
    for i in range(t+1):
        content1=content[854*i:854*i+454]  #跳过第0个时间步，第一个时间步从第854行开始，854会随网格划分格点及单元个数而改变
        content1=content1[3:]              #踢掉tec前面3行头数据
        for i in range(len(content1)):
            content1[i]=content1[i].split()
        content1=pd.DataFrame(content1)
        content_1=content1.ix[obs_Num,[0,1,2,3,4]]
        value=content_1.values
        x=np.vstack((x,value))

    x=x[1+len(obs_Num):]
    x=np.array(x)
    x=np.float64(x)
    np.savetxt(r'E:\ENKF_LabGasInjec2\true_obs\obs_%d.txt' % t,x)



#对观测值进行误差扰动，产生观测值样本空间，由于返回字典，故不进行txt存储，在主程序中直接调用该函数即可
def generate_obs(time_step,obs_num,varR,N):
    args_obs_30=r'E:\ENKF_LabGasInjec2\true_obs\obs_30.txt'
    f=open(args_obs_30,'r')
    content=f.readlines()
    f.close()
    for i in range(len(content)):
        content[i]=content[i].split()
    obs=pd.DataFrame(content)
    obs=obs[[3,4]]
    obs=np.array(obs.values)
    obs=np.float64(obs)
    obs_p1=np.zeros([time_step,obs_num])
    obs_p2=np.zeros([time_step,obs_num])
    for i in range(len(obs)):
        li_num=(i)/obs_num
        col_num=(i)%obs_num
        line=obs[i]
        obs_p1[li_num,col_num]=line[0]
        obs_p2[li_num,col_num]=line[1]

    # # #在原始输出的基础上，进行样本之间的误差扰动，最终输出3维字典，第一维键为时间步，第二维键为观测点序号，第三维为键值，为20个样本的观测值
    obs_Pressure1={}
    obs_Pressure2={}
    for x in range(1,time_step+1):
        tobs1={}
        tobs2={}
        for y in range(1,obs_num+1):
            obs_value1={}
            obs_value2={}
            for z in xrange(N):
                obs_value1[z]=obs_p1[x-1,y-1]+np.sqrt(varR)*np.random.standard_normal()
                obs_value2[z]=obs_p2[x-1,y-1]+np.sqrt(varR)*np.random.standard_normal()
            tobs1[y]=obs_value1
            tobs2[y]=obs_value2
        obs_Pressure1[x]=tobs1
        obs_Pressure2[x]=tobs2
    return obs_Pressure1,obs_Pressure2


if __name__=='__main__':
    read_write_Ki()
    win32api.ShellExecute(0,'open',args_exe,'H2_Permeability_GasPressure',args,1)
    time.sleep(20)
    read_trueobs(time_step,obs_Num)   #如果只修改观测点，不修改真实参数分布，则只需要执行该步
