import datetime
def to_datetime(x):
    tempt = datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S %Z') + datetime.timedelta(hours = 8)
    return tempt.hour*100 + tempt.minute

def time_period(t):
    if t >= 2300 or t < 300:
        return 0
    elif t >= 300 and t < 700:
        return 1
    elif t >= 700 and t < 1100:
        return 2
    elif t >= 1100 and t < 1500:
        return 3
    elif t >= 1500 and t < 1900:
        return 4
    elif t >= 1900 and t < 2300:
        return 5

def Addressing_Data(v_info, records, student_info, name):
    import datetime
    records['time'] = list(map(to_datetime, records['created_at']))

    total_spent_time = [] # 總觀看時間
    total_watch_video_time = [] # 觀看的總影片時間

    length_l = list(v_info['meta'])# length of each lecture
    length_l = [int(i.split('n=>')[1].split('}')[0]) for i in length_l]

    sf = []
    period = [[0 for i in range(len(student_info['student_id']))] for i in range(6)]

    forward_sec = []
    backward_sec =[]
    forward_times = []
    backward_times =[]
    pf = [] # pause freq
    backward_records = records[(records['start'] - records['end'] >= 5) & (records['playback_rate'] ==0)]
    forward_records = records[(records['start'] - records['end'] <= -5) & (records['playback_rate'] ==0)]
    pause_records = records[((records['start'] - records['end']).abs() < 5)]

    j = 0
    for i in student_info['student_id']:
        watch_record_i = records[records['student_id'] == int(i)]
        
        ## 計算總觀看時間
        real_watch_i = watch_record_i[(watch_record_i['end'] > watch_record_i['start']) & (watch_record_i['playback_rate'] != 0)]# 抓出有在看的資料
        video_time_i = real_watch_i['end'] - real_watch_i['start']# 觀看紀錄 的 影片時間(end - start)
        total_watch_video_time.append(sum(video_time_i))
        total_spent_time.append(sum(video_time_i/real_watch_i['playback_rate']))

        ## 計算平均撥放次數
        wf = [] # each video watch freq
        for vi, vl in zip(v_info['id'], length_l):
            record_ji = watch_record_i[(watch_record_i['video_id'] == vi) & (watch_record_i['playback_rate'] != 0)]
            wf.append(sum(record_ji['end'] - record_ji['start'])/vl)
            
            if len(record_ji) != 0:
                for record_index in range(len(record_ji)):
                    record_real_watch_time = (record_ji.iloc[record_index]['end'] - record_ji.iloc[record_index]['start'])/record_ji.iloc[record_index]['playback_rate']
                    first_watch = record_ji.iloc[record_index]['time']
                    #print((first_watch))
                    p = time_period(int(first_watch))
                    #print('time: %d, p = %d' %(first_watch, p))
                    period[p][j] += record_real_watch_time
                    #print(min(record_ji['created_at']).index)
        j += 1
        sf.append(sum(wf)/len(wf))  

        # backwards
        backward_records_i = backward_records[backward_records['student_id'] == int(i)]
        backward_times.append(len(backward_records_i))
        backward_sec.append(sum(backward_records_i['start'] - backward_records_i['end']))
        
        # forwards
        forward_records_i = forward_records[forward_records['student_id'] == int(i)]
        forward_times.append(len(forward_records_i))
        forward_sec.append(sum(forward_records_i['end'] - forward_records_i['start']))

        # pause
        record_i = pause_records[(pause_records['student_id'] == int(i))]
        #display(record_i)
        pf.append(len(record_i))


    student_info['total_watch_time'] = total_spent_time
    student_info['watch_freq'] = sf
    student_info['backward_sec'] = backward_sec
    student_info['backward_times'] = backward_times
    student_info['forward_sec'] = forward_sec
    student_info['forward_times'] = forward_times
    student_info['pause_freq'] = pf

    for i in range(len(period)):
        student_info['period %d' %i] = period[i]
    # student_info['watched_video'] = sum(np.array(period[i]) for i in range(6))

    ## 計算撥放速度 OK
    total_spent_time = [x if x!= 0 else 1 for x in total_spent_time]
    avg_playback_rate = [i/j for (i,j) in zip(total_watch_video_time, total_spent_time)]
    student_info['avg_playback_rate'] = avg_playback_rate

    student_info.to_excel(name+".xlsx")
    #return student_info


import pandas as pd
import numpy as np

DSAP107 = ['DSAP107_grades.csv', 'DSAP107_record.xlsx', 'DSAP107_video.xlsx']
DSAP108 = ['DSAP108_grades.csv','DSAP108_record.xlsx', 'DSAP108_video.xlsx']
OR107 = ['OR108_grades.csv','OR108_record.xlsx', 'OR108_video.xlsx']
OR108 = ['OR107_grades.csv','OR107_record.xlsx', 'OR107_video.xlsx']

def read_files(file_lis):
    file_dict = {}
    for f in file_lis:
        print("reading...",f)
        if('csv' in f):
            file_dict[f.split("_")[1][:-4]] = pd.read_csv('data/'+f)
        else:
            file_dict[f.split("_")[1][:-5]] = pd.read_excel('data/'+f)
    return file_dict

DSAP107_file_dict = read_files(DSAP107)
DSAP108_file_dict = read_files(DSAP108)
OR107_file_dict = read_files(OR107)
OR108_file_dict = read_files(OR108)

def new_data(file_dict, name):
    Addressing_Data(file_dict['video'], file_dict['record'], file_dict['grades'], name=name)

print("processing...","DSAP107")
new_data(DSAP107_file_dict, 'DSAP107')
print("processing...","DSAP108")
new_data(DSAP108_file_dict, 'DSAP108')
print("processing...","OR107")
new_data(OR107_file_dict, 'OR107')
print("processing...","OR108")
new_data(OR108_file_dict, 'OR108')


        
