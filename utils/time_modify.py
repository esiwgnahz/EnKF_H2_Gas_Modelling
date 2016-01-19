#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'zq'

##只能从时间t=1依次向后更新，不能随机更新
# def time_modify(t,i):
#     args_tim=r'E:\ENKF_LabGasInjec2\gas_%d\H2_Permeability_GasPressure.tim' % i
#     deltat=t-1
#     fp=open(args_tim)
#     s=fp.read()
#     fp.close()
#     a=s.split('\n')
#     time_num_start_1=5+deltat-1
#     a.insert(time_num_start_1,'  1     500')
#     time_num_end_1=time_num_start_1+1
#     str='   %d' % (500*t)
#     a[time_num_end_1+1]=str
#
#     time_num_start_2=time_num_end_1+1+8+deltat
#     a.insert(time_num_start_2,'  1     500')
#     time_num_end_2=time_num_start_2+1
#     a[time_num_end_2+1]=str
#     s='\n'.join(a)
#     fw=open(args_tim,'w')
#     fw.write(s)
#     fw.close()

def time_modify(t,i):
    args_tim=r'E:\ENKF_LabGasInjec2\gas_%d\H2_Permeability_GasPressure.tim' % i
    with open(args_tim,'r') as f:
        content=f.readlines()
        line_modify_1=content[4]
        line_modify_2=content[6]
        modify_1=line_modify_1.split()
        modify_1[0]='{0}'.format(t)
        line_modify_1=' '.join(modify_1[i] for i in range(len(modify_1)))+'\n'
        modify_2=line_modify_2.split()
        modify_2[0]='{0}'.format(t*500)
        line_modify_2=' '.join(modify_2[i] for i in range(len(modify_2)))+'\n'
        content[4]=line_modify_1
        content[6]=line_modify_2
    with open(args_tim,'w') as f:
        for line in content:
            f.write(line)

if __name__=='__main__':
    time_modify(5,4)