
from calendar import month
import os, sys, shutil, json
import os.path as osp
import pandas as pd
import numpy as np
from yaml import dump
import os, sys, shutil, json
import os.path as osp
import pandas as pd
import numpy as np
from tqdm import tqdm
import random
import datetime
import matplotlib.pyplot as plt


first_season = ['January','February','March']
second_season = ['April','May','June']
third_season = ['July','August','September']
forth_season = ['October','November','December']

def get_season(month):
    if month in first_season:
        return 1
    if month in second_season:
        return 2
    if month in third_season:
        return 3
    if month in forth_season:
        return 4



def read_json(json_path):
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    sample_list = json_data['reviews']
    review_date_list = []

    begin_year = 2088
    end_year = 1888

    for sample in sample_list:
        review_content = sample['review']
        date_list = sample['date'].split()[-3:]
        month = date_list[0]
        year = int(date_list[2])
        if begin_year > year:
            begin_year = year
        if end_year < year:
            end_year = year
    print(begin_year,end_year)
    x_data = []
    y_data = []
    for index in range(begin_year,end_year+1):
        for season in range(1,5):
            x_data.append(str(index)[2:]+''+'0'+str(season))
    print(len(x_data))
    # get the y_data
    for index in range(len(x_data)):
        y_data.append(0)
    for sample in sample_list:
        date_list = sample['date'].split()[-3:]
        month = date_list[0]
        year = int(date_list[2])
        tmp = get_season(month)
        x = (year - begin_year)*4+tmp-1
        y_data[x]+=1
    return x_data[2:-2],y_data[2:-2]
        

def get_the_pic(x_data,y_data):

    plt.figure(figsize=(18,18))
    for i in range(len(x_data)):
        plt.bar(x_data[i],y_data[i])
    plt.title("Sales Analysis")
    plt.xlabel("times")
    plt.ylabel("sales")
    
    plt.show()
    plt.savefig('year_to_sell_amount.jpg')


if __name__ == '__main__':
    json_path = '/cloud/cloud_disk/users/huh/nlp/smart_home/dataset/coped_data/B07DMMG7QY.json'
    x_data,y_data = read_json(json_path)
    get_the_pic(x_data,y_data)
