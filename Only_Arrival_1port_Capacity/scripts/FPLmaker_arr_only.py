#!/usr/bin/env python
# coding: utf-8

# In[18]:

#ruatm: 3, arr_Vport: 1

import matplotlib
matplotlib.use('nbagg')
import matplotlib.animation as anm
import matplotlib.pyplot as plt
import math
import matplotlib.patches as patches
import numpy as np
import time
import random
import pandas as pd
import copy
from datetime import datetime



#2024/1/29　修正　delayの与え方を変更: delay = t→t+1


# In[19]:


class RUATM:                                                                                            #UATM 0=A 1=B 2=C 3=D
    def __init__(self, airspace_max):
        self.airspace_max = airspace_max             #  10, 10, 10, 10

        
        
        
class FlightPlan:
    def __init__(self, ruatm_list, num_route, sim_time, max_flight_time, flight_num):
        self.num_ruatm = len(ruatm_list) #RUATM数
        self.ruatm_list = ruatm_list #RUATMのリスト
        self.num_route  =num_route #各RUATMのルート本数
        self.sim_time = sim_time #シミュレーション時間
        self.max_flight_time = max_flight_time #各フライトのMAX時間
        self.flight_num = flight_num
        
    def making_fpl(self):
        self.fpl_data = pd.DataFrame()
        for i in range(self.flight_num): 
            one_fpl = self.one_fpl(i)            #one_fplを呼び出し
            self.fpl_data = pd.concat([self.fpl_data, one_fpl])
            
        return self.fpl_data
    
    def one_fpl(self, i):
        self.dep = random.choice(self.ruatm_list) #出発RUATM
        self.route = random.randint(self.dep*self.num_route, (self.dep+1)*self.num_route -1) #ルート

        self.dep_time = random.randint(0, self.sim_time-self.max_flight_time) #出発時刻
#         self.arr_time = random.randint(self.dep_time+600, self.dep_time+self.max_flight_time) #到着時刻
        self.arr_time = self.dep_time + (self.route + 1 - self.num_route*self.dep)*1200 #到着時間はランダムではなく、ルートごとに設定することに変更。1200,2400,3600 のどれか
        self.data = pd.DataFrame([[i, self.dep, self.dep_time, self.route, self.arr_time]], 
                     columns=["flight_id", "dep", "dep_time", "route", "arr_time"], index=[i])
        return self.data

        
        
        
        
class EnrouteCheck:
    def __init__(self, fpl_data, ruatm_num, sim_time):
        self.fpl_data = fpl_data
        self.flight_num = len(self.fpl_data)
        self.ruatm_num = ruatm_num
        self.sim_time = sim_time
        self.current_aircraft_num = np.zeros(self.ruatm_num) # RUATMの数
    
    def flight(self, flight_num):
        self.flight_data = np.zeros((0, flight_num)) #number of flight

        self.ruatm_onetime_data = np.full(flight_num, 10) #出発前のフライトは10とする
        self.ruatm_data = np.zeros((0, self.ruatm_num))

        for t in range(self.sim_time): 
            self.ruatm_onetime_data = self.flight_step(t, self.ruatm_onetime_data)  #flight_stepを呼び出し
            self.flight_data = np.append(self.flight_data, self.ruatm_onetime_data.reshape(1, self.flight_num), axis=0) #時刻tでのflight_dataが完成
    
            self.aircraft_num = np.zeros(self.ruatm_num)
            for j in range(self.flight_num):
                if self.ruatm_onetime_data[j] < self.ruatm_num:
                    self.aircraft_num[self.ruatm_onetime_data[j]] += 1
                else:
                    pass

            self.ruatm_data = np.append(self.ruatm_data, self.aircraft_num.reshape(1, self.ruatm_num), axis=0)
            
        return self.flight_data, self.ruatm_data
    
    
    def flight_step(self, t, ruatm_onetime_data):
        self.time = t
        self.ruatm_onetime_data = ruatm_onetime_data
        for i in range(self.flight_num):
            if self.fpl_data.at[i, 'dep_time'] == self.time:                           #t=DEPtimeのとき
                self.ruatm_onetime_data[i] = self.fpl_data.at[i, 'dep']
            elif self.fpl_data.at[i, 'arr_time'] == self.time:                          #t=ARRtimeのとき
                self.ruatm_onetime_data[i] = 100                                      #到着後のフライトは100とする
            else:
                pass
        return self.ruatm_onetime_data
    

    
    
    
class ArrCheck:
    def __init__(self, fpl_data, ruatm_num, route_num, sim_time):
        self.fpl_data = fpl_data
        #self.flight_num = len(self.fpl_data)
        self.ruatm_num = ruatm_num
        self.route_num = route_num
        self.sim_time = sim_time
        self.current_aircraft_num = np.zeros(self.ruatm_num) # RUATMの数
        self.flight_counter = np.zeros(3)
        
    def flight(self, flight_num):
        self.flight_num = flight_num
        self.flight_data = np.zeros((0, self.flight_num)) #number of flight

        self.ruatm_onetime_data = np.full(self.flight_num, 10) #到着前のフライトは10とする
        self.ruatm_data = np.zeros((0, self.ruatm_num))

        for t in range(self.sim_time):
            self.ruatm_onetime_data = self.flight_step(t, self.ruatm_onetime_data)  #flight_stepを呼び出し
            self.flight_data = np.append(self.flight_data, self.ruatm_onetime_data.reshape(1, self.flight_num), axis=0) #時刻tでのflight_dataが完成
    
            self.aircraft_num = np.zeros(self.ruatm_num)
            for j in range(self.flight_num):
                if self.ruatm_onetime_data[j] < self.ruatm_num:
                    self.aircraft_num[self.ruatm_onetime_data[j]] += 1
                    self.flight_counter[self.ruatm_onetime_data[j]] += 1
                else:
                    pass

            self.ruatm_data = np.append(self.ruatm_data, self.aircraft_num.reshape(1, self.ruatm_num), axis=0)
        
        #print(f'到着機数: {self.flight_counter}')
        return self.flight_data, self.ruatm_data
    
    
    def flight_step(self, t, ruatm_onetime_data):
        self.time = t
        self.ruatm_onetime_data = ruatm_onetime_data
        for i in range(self.flight_num): 
#         for i in self.fpl_data['flight_id']: #cooperative_fcfsだとFPLが書き換えられているから、変更
            if self.fpl_data.at[i, 'arr_time'] == self.time:                          #t=ARRtimeのとき、self.ruatm_onetime_data[i]にdepを格納
                self.ruatm_onetime_data[i] = self.fpl_data.at[i, 'dep']                                 
            else:
                self.ruatm_onetime_data[i] = 10       #到着後のフライトも10に設定
        return self.ruatm_onetime_data
    
    
    def demand_calc(self, ruatm_data, bin_size=120):
        self.time_bin = np.zeros((int(self.sim_time/bin_size), self.ruatm_num))   #bin_size間隔のタイムビンを作成
        
        for k in range(len(self.time_bin)):
            self.bin_flight_num = np.sum(self.ruatm_data[bin_size*k: bin_size*(k+1)], axis=0)
            self.time_bin[k] = self.bin_flight_num
        
        return self.time_bin
        

