# EnKF_H2_Gas_Modelling


      This is my first version of data assimilation codes using EnKF with OpenGeoSys, and this case considers water-gas copuling     
      condition.
      main_restart.py is the main function which conducts the calculation of EnKF, and utils is the package which can be called by 
      main_restart.py. Gas_injection model is the model settings using an open-source software called OpenGeoSys.
      This version is unsatble and also i cannot get a convergence result eventually, and i just want to construct a framework for this 
      problem. In the near future, i will work hard to study OpenGeoSys and try to understand more and more source codes written in C++.
      Further, this calculation codes writing by Python have a lot needing to be optimized, like the right use of classes enabling the  
      realizations of OOP concept. 
