'''
Created on 30 juin 2017

@author: Philippenko
'''

from timeit import default_timer as timer
import pandas as pd
from storage.save import save_double_list, save_segments
import datetime
from storage.load import load_double_list, load_segmentation
from segmentation import Segmentation
from segmentation_construction import union

# 0er = jaune !!!
# 1eme = t-shirt pale !!!

filenames=['1-right-leg-7_2017-03-09T14.57.14.327_D5ECF7066E47_Accelerometer_50.0Hz.csv','2-right-leg-8_2017-03-09T14.59.09.810_CC7A3221D5C1_Accelerometer_50.0Hz.csv']
def prepare_data():   
    
    start = timer()
    print("#### \t Starting ! ")  
    
    for i in range(2):
        data=pd.DataFrame({})
    
        print("Worker ", i)
        filename=filenames[i]
        data = pd.concat([data,pd.DataFrame(pd.read_csv(filename))])
        
        data=data.reset_index(drop=True)
        data = data.drop(['epoch (ms)', 'elapsed (s)'], 1)
        
        print("SSQ segmentation_construction")
        col=[]
        time=[]
        origine=data.iloc[0,0]
        for j in range(len(data)):
                col.append(data["x-axis (g)"][j]**2+data["y-axis (g)"][j]**2+data["z-axis (g)"][j]**2)
                if i==0:
                    time.append(datetime.datetime.strptime(data.iloc[j,0], '%Y-%m-%dT%H:%M:%S.%f')+
                                datetime.timedelta(seconds=3*60+6))
                else:
                    time.append(datetime.datetime.strptime(data.iloc[j,0], '%Y-%m-%dT%H:%M:%S.%f')+
                                datetime.timedelta(seconds=3*60+8))
                    
        data["SSQ"]=col
        data["Time"]=time
     
        serie=list(data["SSQ"])
        save_double_list(serie,list(time),"forecsys_data{0}.csv".format(i))
        
    end=timer()
    
    print("Running time :", end-start)
    
    
def prepare_test_data():
    for j in range(12):
        prepare_data_j(j)
        
def prepare_data_j(j, started=False):
    filepath="forecsys_data\\{0}".format("Worker{0}".format(j))
    filename="forecsys_data{0}.csv".format(j)
    print("Worker :",j)
    (serie,temps)=load_double_list(filename, True)
    if started==False:
        sgmtt=Segmentation(absc=temps, serie=serie,order=4,activity="Worker{0}".format(j),automatic=False, compute=False)
    else:
        sgmtt=load_segmentation(filepath)
        sgmtt2=Segmentation(absc=temps, serie=serie,order=4,activity="Worker{0}".format(j),automatic=False, compute=False)
        (absc,serie,order,activity,sd_serie,breaking_points,segments,average_segment,dispersion_segment)=union(sgmtt,sgmtt2)
        sgmtt=Segmentation(absc=absc,serie=serie,order=order,activity=activity,sd_serie=sd_serie,
                           breaking_points=breaking_points,segments=segments,average_segment=average_segment,
                           dispersion_segment=dispersion_segment)
    sgmtt.store(filepath)
    sgmtt.display_segmentation(filepath)
    rec=len(sgmtt.get_breaking_points())-1
    save_segments(rec, filepath+"\\info.txt")
        
def recompute_stat(j):
    filepath="forecsys_data\\{0}".format("Worker{0}".format(j))
    sgmtt=load_segmentation(filepath)
    rec=len(sgmtt.get_breaking_points())-1
    save_segments(rec, filepath+"\\info.txt")
        