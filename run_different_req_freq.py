import os

CUR_FPATH = os.path.abspath(__file__)
CUR_FDIR = os.path.dirname(CUR_FPATH)

# chdir to the directory of this script
os.chdir(CUR_FDIR)


import threading
from proxy_env3 import ProxyEnv3


class Task: 

    # 根据给定的算法配置来配置代理环境的参数
    def algo(self,algo_conf):
        self.env=ProxyEnv3()
        confs=[
            'mech_type',
            'scale_num',
            'scale_down_exec',
            'scale_up_exec',
            'sche'
        ]
        for i,conf in enumerate(confs[:5]):
            self.env.config["mech"][conf][algo_conf[i][0]]=algo_conf[i][1]
        for f in algo_conf[5]:
            filter_name=list(f.keys())[0]
            attr=f[filter_name]
            self.env.config["mech"]['filter'][filter_name]=attr
        # self.env.config["mech"]['mech_type']
        # self.env.config["mech"]['scale_num'][algo_conf[0][0]]=algo_conf[0][1]
        # self.env.config["mech"]['scale_down_exec'][algo_conf[1][0]]=algo_conf[1][1]
        # self.env.config["mech"]['scale_up_exec'][algo_conf[2][0]]=algo_conf[2][1]
        # self.env.config["mech"]['sche'][algo_conf[3][0]]=algo_conf[3][1]
        return self
        
    def config(self,config_cb):
        config_cb(self.env.config)
        return self
        
    def run(self):
        self.env.reset()
        
        state,score,stop,info=self.env.step(1)
        print(state,score,stop,info)
        self.env.reset()
        return self


# req_freqs=["low"]
# req_freqs=["middle"]
req_freqs=["high"]

algos=[
    # mechtype, scale_num, scale_down_exec, scale_up_exec, sche

    [['scale_sche_joint',''],["hpa",""],["default",""],["least_task",""],["pos",""],[{'careful_down':''}]],
    # [['scale_sche_joint',''],["hpa",""],["default",""],["least_task",""],["bp_balance",""],[{'careful_down':''}]],

    # [['scale_sche_joint',''],["temp_scaler",""],["default",""],["least_task",""],["pos",""],[{'careful_down':''}]],
    # [['scale_sche_joint',''],["temp_scaler",""],["default",""],["least_task",""],["bp_balance",""],[{'careful_down':''}]],

    # [['scale_sche_separated',''],["hpa",""],["default",""],["least_task",""],["greedy",""],[{'careful_down':''}]],
    # [['scale_sche_separated',''],["lass",""],["default",""],["least_task",""],["greedy",""],[{'careful_down':''}]],

    # [['no_scale',''],['no',''],["default",""],['no',''],['faasflow','']],
    # [['no_scale',''],["no",""],["default",""],["no",""],["consistenthash",""]],
    # ["lass","lass","rule"],
    # ["fnsche","fnsche","fnsche"],
    # ["faasflow","faasflow","faasflow"],
]

ts=[]

for req_freq in req_freqs:    
    for algo in algos:
        def cb(config):
            config["request_freq"]=req_freq
        def task():
            Task() \
                .algo(algo) \
                .config(cb) \
                .run()
        t = threading.Thread(target=task, args=())
        t.start()
        ts.append(t)

for t in ts:
    t.join()

    