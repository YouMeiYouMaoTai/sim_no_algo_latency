import json
import os
import matplotlib.pyplot as plt
import numpy as np


FRAME_IDX_FRAME = 0
FRAME_IDX_RUNNING_REQS = 1
FRAME_IDX_NODES = 2
FRAME_IDX_REQ_DONE_TIME_AVG = 3
FRAME_IDX_REQ_DONE_TIME_STD = 4
FRAME_IDX_REQ_DONE_TIME_AVG_90P = 5
FRAME_IDX_COST = 6
FRAME_IDX_SCORE = 7
FRAME_IDX_DONE_REQ_COUNT = 8

# 加载json文件
def load_json_files(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    data = []
    for file in json_files:
        with open(os.path.join(folder_path, file), 'r') as f:
            data.append(json.load(f))
    return data

# 读取json文件数据，传出list
def extract_data(json_data):
    tasks_count = []
    cost_performance = []
    
    for record in json_data:
        task = []
        cost = []

        frames = record['frames']
        for frame in frames:
            index = frame[FRAME_IDX_FRAME]
            current_tasks = len(frame[FRAME_IDX_RUNNING_REQS])
            avg_completion_time = frame[FRAME_IDX_REQ_DONE_TIME_AVG]
            avg_cost = frame[FRAME_IDX_COST]
            
            task.append((index, current_tasks))
            if avg_completion_time + avg_cost != 0:
                cost.append((index, 1 / (avg_completion_time * avg_cost)))
            else:
                cost.append((index, 0))
        tasks_count.append(task)
        cost_performance.append(cost)
    
    return tasks_count, cost_performance

# 画图
def plot_2d_list(tasks_count, cost_performance, json_data):
    plt.figure(figsize=(12, 6))

    keys = []
    for i in json_data:
        keys.append(i['record_name'][:-24])

    plt.subplot(2, 1, 1)
    for i, sublist in enumerate(tasks_count):
        x_values = [item[0] for item in sublist]
        y_values = [item[1] for item in sublist]
        avg_value = np.mean(y_values)
        plt.plot(x_values, y_values, label=f'{keys[i]} || AVG: {avg_value:.2f}')

    plt.xlabel('frame')
    plt.ylabel('Current Task Count')
    plt.title('Current Task Count Over Time')
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2)
    for i, sublist in enumerate(cost_performance):
        x_values = [item[0] for item in sublist]
        y_values = [item[1] for item in sublist]
        avg_value = np.mean(y_values)
        plt.plot(x_values, y_values, label=f'{keys[i]} || AVG: {avg_value:.2f}')
    
    plt.xlabel('frame')
    plt.ylabel('Cost performance')
    plt.title('Cost Performance Over Time')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()


def main(folder_path):

    json_data = load_json_files(folder_path)

    tasks_count, cost_performance = extract_data(json_data)
    plot_2d_list(tasks_count, cost_performance, json_data)


if __name__ == "__main__":
    folder_path = ".//serverless_sim//records"
    main(folder_path)