#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import matplotlib.animation as anm
import matplotlib.pyplot as plt
import math
import matplotlib.patches as patches
import numpy as np
from datetime import datetime

class Graph:
    def __init__(self):
        pass
    
    def mid_air(self, data, title, seed, save):
        data = data
        fig = plt.figure(figsize=(9,7))
        ax = fig.add_subplot(111)
        x = np.arange(10800)

        #ax.set_aspect('equal')      

        ax.set_xlim(0, 10800)                  
        ax.set_ylim(0, 20) 

        ax.set_xlabel("time [s]",fontsize=23)                 
        ax.set_ylabel("number of aircraft in mid air",fontsize=23)

        ax.set_xticks(np.linspace(0, 10000, 5))
        ax.set_yticks(np.linspace(0, 20, 5))
        plt.tick_params(labelsize=20)

        plt.title(title, fontsize=24)
        plt.grid(True)
        plt.rcParams['font.family'] = 'Times New Roman' # Fonts
        plt.plot(x, data[:,0], marker="o", markersize=1, color='tab:blue', label='RUATM A')
        plt.plot(x, data[:,1], marker="o", markersize=1, color='tab:orange', label='RUATM B')
        plt.plot(x, data[:,2], marker="o", markersize=1, color='tab:green', label='RUATM C')
        #plt.plot(x, data[:,3], marker="o", markersize=1, color='tab:red', label='RUATM D')

        ax.legend(bbox_to_anchor=(1, 1), loc='upper right', fontsize=15)

        flight_png = "data/" + title + f"_{seed}" + f"_result_{datetime.now():%Y%m%d%H%M%S}.png"
        if save == True:
            plt.savefig(flight_png)
        plt.show()
        
        
        
    def vport(self, data, title, seed, save):
        data = data
        fig = plt.figure(figsize=(9,7))
        ax = fig.add_subplot(111)
        x = np.arange(10800)

        #ax.set_aspect('equal')      

        ax.set_xlim(0, 10800)                  
        ax.set_ylim(0, 5) 

        ax.set_xlabel("time [s]",fontsize=23)                 
        ax.set_ylabel("number of aircraft in mid air",fontsize=23)

        ax.set_xticks(np.linspace(0, 10000, 5))
        ax.set_yticks(np.linspace(0, 5, 6))
        plt.tick_params(labelsize=20)

        plt.title(title, fontsize=24)
        plt.grid(True)
        plt.rcParams['font.family'] = 'Times New Roman' # Fonts
        plt.plot(x, data[:,0], marker="o", markersize=1, color='tab:blue', label='RUATM A')
        plt.plot(x, data[:,1], marker="o", markersize=1, color='tab:orange', label='RUATM B')
        plt.plot(x, data[:,2], marker="o", markersize=1, color='tab:green', label='RUATM C')
        #plt.plot(x, data[:,0]+data[:,1]+data[:,2], marker="o", markersize=1, color='tab:red', label='RUATM D')

        ax.legend(bbox_to_anchor=(1, 1), loc='upper right', fontsize=15)

        flight_png = "data/" + title + f"_{seed}" + f"_result_{datetime.now():%Y%m%d%H%M%S}.png"
        if save == True:
            plt.savefig(flight_png)
        plt.show()
        
  

    def vport_bin(self, data_name, title, seed, sim_time=10800, bin_size=720, save=False):
        data = data_name
        fig = plt.figure(figsize=(9,6.5))
        ax = fig.add_subplot(111)
        x = np.linspace(bin_size/2, sim_time-(bin_size/2), int(sim_time/bin_size), dtype=int)
#         data_max = int(np.max(np.sum(data, axis=1)))
        data_max = 7

        #ax.set_aspect('equal')  
        plt.rcParams['font.family'] = 'Times New Roman' # Fonts
        ax.set_xlim(0, sim_time)                  
        ax.set_ylim(0, data_max+1) 

        ax.set_xlabel('time [min]',fontsize=23)                 
        ax.set_ylabel('demand',fontsize=23)

        ax.set_xticks(np.linspace(0, sim_time, int(sim_time/bin_size) + 1))
        ax.set_xticklabels(np.linspace(0, sim_time/60, int(sim_time/bin_size) + 1, dtype=int))
        ax.set_yticks(np.linspace(0, data_max+1, data_max+2))
        ax.set_yticklabels(np.linspace(0, data_max+1, data_max+2, dtype=int))
        plt.tick_params(labelsize=13)

        plt.title(title, fontsize=24)
        plt.grid(True)
        plt.hlines(y=3, xmin=0, xmax=sim_time, color='tab:red', linewidth=2)
        plt.bar(x, data[:, 0], color='tab:blue', label='RUATM A', width=bin_size/1.2, edgecolor="black", linewidth=1)
        plt.bar(x, data[:, 1], color='tab:orange', label='RUATM B', width=bin_size/1.2, edgecolor="black", linewidth=1, bottom=data[:, 0])
        plt.bar(x, data[:, 2], color='tab:green', label='RUATM C', width=bin_size/1.2, edgecolor="black", linewidth=1, bottom=data[:, 0]+data[:, 1])

        ax.legend(bbox_to_anchor=(0, 1), loc='upper left', fontsize=15)

        flight_png = "data/" + title + f"_{seed}" + f"_result_{datetime.now():%Y%m%d%H%M%S}.png"
        if save == True:
            plt.savefig(flight_png)
        plt.show()


