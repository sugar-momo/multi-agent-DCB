#!/usr/bin/env python
# coding: utf-8

# In[18]:


import sys
sys.path.append('scripts/')
from FPLmaker_arr_only import *
from graph import *
from importlib import reload # >= python 3.4


#2024/1/29　修正　delayの与え方を変更: delay = t→t+1


class DCB:
    def __init__(self, airspace_max): #DCBを行う関数
        self.airspace_max = airspace_max
        self.total_delay = np.zeros(4) #総遅延時間
        self.num_delay = np.zeros((0, 4))
    
    
    
    def centralized_fcfs(self, ruatm_id, capacity, sim_time, flight_num, bin_data, bin_size, fpl):  #全部の情報がわかる状態。中央制御的にやる。
        self.ruatm_id = ruatm_id #ruatm_id = 0, 1, 2
        self.capacity = capacity
        self.sim_time = sim_time
        self.flight_num = flight_num
        self.bin_data = bin_data
        self.bin_size = bin_size
        self.fpl = fpl.copy()
        self.delay_memo = np.zeros((0, len(ruatm_id)*2))
        
        
        for i in range(len(self.bin_data)):  #binをループ
            if np.sum(self.bin_data[i]) > self.capacity:  #キャパを超えてるか確認
                self.bin_start_time = self.bin_size * i  #binの開始時刻
                self.bin_end_time = self.bin_size*(i+1)  #binの終了時刻
                self.arr_fpl = self.fpl[(self.bin_start_time < self.fpl['arr_time']) 
                                           & (self.fpl['arr_time'] < self.bin_end_time)] #ビン該当の時刻に到着するフライトを抽出
                self.arr_fpl = self.arr_fpl.sort_values('arr_time', ascending=False)  #到着の遅い順にソート
                
                print(np.sum(self.bin_data[i]) - self.capacity)
                #print(self.bin_start_time/60, self.bin_end_time/60, self.arr_fpl)
                
                self.change_count = 0 #出発変更した機体の数カウントする
                for j in self.arr_fpl['flight_id']: #該当フライトを遅い順に反復
                    if self.change_count >= np.sum(self.bin_data[i]) - self.capacity: break #変更指示数がオーバー数を超えたら終了
                    #if any(i == self.over_flight_id) == False: continue #ownRUATM出発で、現在capacityにかかわっていないものは省く
                    
                    delay = -1 + self.bin_size + self.bin_end_time - self.fpl.at[j, 'arr_time'] #次のbin 終了時刻 - 当該フライトの出発時刻 + 1 ここ注意！！！！！！！！！！！！！
                    self.fpl.at[j, 'dep_time'] += delay  #出発時刻をdelayだけ遅らせる
                    self.fpl.at[j, 'arr_time'] += delay  #到着時刻をdelayだけ遅らせる
                    
                    #メモ用
                    apd_delay = np.zeros(len(ruatm_id)*2)
                    apd_delay[3:6] = np.nan
                    apd_delay[self.fpl.at[j, 'dep']] = delay
                    apd_delay[self.fpl.at[j, 'dep']+3] = j
                    if np.any(self.delay_memo[:, self.fpl.at[j, 'dep']+3] == j):
                        self.delay_memo[np.where(self.delay_memo[:, self.fpl.at[j, 'dep']+3] == j)[0], self.fpl.at[j, 'dep']] += delay
                    else:
                        self.delay_memo = np.append(self.delay_memo, apd_delay.reshape(1, len(ruatm_id)*2), axis=0)
                    self.change_count += 1
            
                delayed_ac = ArrCheck(self.fpl, len(ruatm_id), self.sim_time)
                delayed_vport_flight_data, delayed_vport_ruatm_data = delayed_ac.flight(self.flight_num)
                self.bin_data = delayed_ac.demand_calc(delayed_vport_ruatm_data, bin_size)
        
        self.delay_summary = np.zeros(len(ruatm_id)*3)
        self.delay_summary[:] = np.nan
        self.delay_summary[0:3] = np.sum(self.delay_memo, axis=0)[0:3]  # 0,1,2は合計
        self.delay_summary[3:6] = np.max(self.delay_memo, axis=0)[0:3]  # 3,4,5は最大値
        self.delay_summary[6] = len(np.unique(self.delay_memo[:, 3])) -1
        self.delay_summary[7] = len(np.unique(self.delay_memo[:, 4])) -1
        self.delay_summary[8] = len(np.unique(self.delay_memo[:, 5])) -1
        #self.delay_memo = np.append(self.delay_memo, np.sum(dcb.delay_memo, axis=0).reshape(1, len(ruatm_id)+1), axis=0) #delayの合計
        #self.delay_memo[-1, -1] = len(np.unique(self.delay_memo[:, -1])) -1
        
        return self.fpl, self.bin_data
    
    
    
    
    def distributed_fcfs(self, ruatm_id, capacity, sim_time, flight_num, bin_data, bin_size, fpl):  #分散型
        self.ruatm_id = ruatm_id # ruatm_id = one of them
        self.capacity = capacity # = 1
        self.sim_time = sim_time
        self.flight_num = flight_num
        self.bin_data = bin_data
        self.bin_size = bin_size # 9
        self.fpl = fpl.copy()
        self.ruatm_num = 3
        self.delay_memo = np.zeros((0, 2))
        apd_delay = np.zeros(2)
        
        
        for i in range(len(self.bin_data)):  #binをループ
            if self.bin_data[i, self.ruatm_id] > self.capacity:  #キャパを超えてるか確認
                self.bin_start_time = self.bin_size * i  #binの開始時刻
                self.bin_end_time = self.bin_size*(i+1)  #binの終了時刻
                self.arr_fpl = self.fpl[(self.bin_start_time < self.fpl['arr_time']) 
                                           & (self.fpl['arr_time'] < self.bin_end_time)] #ビン該当の時刻に到着するフライトを抽出
                self.arr_fpl = self.arr_fpl.sort_values('arr_time', ascending=False)  #到着の遅い順にソート
                
                print(self.bin_data[i, self.ruatm_id] - self.capacity)
                #print(self.bin_start_time/60, self.bin_end_time/60, self.arr_fpl)
                
                self.change_count = 0 #出発変更した機体の数カウントする
                
                for j in self.arr_fpl['flight_id']: #該当フライトを遅い順に反復
                    if self.change_count >= self.bin_data[i, self.ruatm_id] - self.capacity: break #変更指示数がオーバー数を超えたら終了
                    if self.arr_fpl.at[j, 'dep'] != self.ruatm_id: continue #該当ruatmの機体じゃなかったらスキップ
                        
                    delay = -1 + self.bin_size + self.bin_end_time - self.fpl.at[j, 'arr_time'] #次のbin 終了時刻 - 当該フライトの出発時刻 + 1 ここ注意！！！！！！！！！！！！！
                    self.fpl.at[j, 'dep_time'] += delay  #出発時刻をdelayだけ遅らせる
                    self.fpl.at[j, 'arr_time'] += delay  #到着時刻をdelayだけ遅らせる
                    
                    #メモ用
                    apd_delay = np.zeros(2)
                    apd_delay[0] = delay
                    apd_delay[-1] = j
                    if np.any(self.delay_memo[:, -1] == j):
                        self.delay_memo[np.where(self.delay_memo[:, -1] == j)[0], 0] += delay
                    else:
                        self.delay_memo = np.append(self.delay_memo, apd_delay.reshape(1, 2), axis=0)
                    self.change_count += 1
            
                delayed_ac = ArrCheck(self.fpl, self.ruatm_num, self.sim_time)
                delayed_vport_flight_data, delayed_vport_ruatm_data = delayed_ac.flight(self.flight_num)
                self.bin_data = delayed_ac.demand_calc(delayed_vport_ruatm_data, bin_size)
        
        self.delay_summary = np.zeros(3)
        if len(self.delay_memo) == 0:
            self.delay_memo = np.zeros((1, 2))
            self.delay_summary[2] = 0
        else:
            self.delay_summary[2] = len(np.unique(self.delay_memo[:, -1]))
        self.delay_summary[0] = np.sum(self.delay_memo, axis=0)[0]  # 0は合計
        self.delay_summary[1] = np.max(self.delay_memo, axis=0)[0]  # 1は最大値
        return self.fpl, self.bin_data
