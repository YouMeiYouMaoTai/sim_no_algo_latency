use crate::{
    actions::{ESActionWrapper, RawAction},
    algos::ContainerMetric,
    config::Config,
    fn_dag::FnId,
    mechanism::Mechanism,
    node::NodeId,
    request::ReqId,
    scale::num::{hpa::HpaScaleNum, lass::LassScaleNum, no::NoScaleNum, ScaleNum},
    sim_env::SimEnv,
    sim_run::Scheduler,
};
use enum_as_inner::EnumAsInner;
use moka::sync::Cache;
use std::{
    cell::RefMut, collections::{BTreeMap, VecDeque}, fs::OpenOptions, time::{SystemTime, Instant}
};
use std::io::Write;

impl SimEnv {
    /// raw_action[0] container count
    pub fn step_es(&mut self, raw_action: ESActionWrapper) -> (f32, String) {
        self.avoid_gc();

        // 只有确定了下一个action，才会有可以返回的state

        let mut avg_ex_time = 0;

        loop {
            // 进行帧开始时处理
            self.on_frame_begin();

            // 生成新的请求，并添加到环境对象的请求映射中
            self.req_sim_gen_requests();

            // 新请求生成之后将系统中请求和节点更新到最新状态
            self.help.mech_metric_mut().on_new_req_generated(self);

            // MARK 测试执行时间快慢程度
            let begin_time = Instant::now();

            // 获得 扩容、缩容、调度 的指令
            let (ups, downs, sches) = self.new_mech.step(self, raw_action.clone());

            // MARK 测试执行时间快慢程度
            let end_time = Instant::now();
            let (sche_name, _) = self.help.config().mech.sche_conf();
            let (scaler_name, _) = self.help.config().mech.scale_num_conf();
            let file_name = format!("{}{}_{}{}", "D:\\Desktop\\Program\\test_records\\ex_time\\", scaler_name, sche_name, "_ex_time.txt");
            let duration = end_time.duration_since(begin_time);
            let duration_ms = duration.as_millis();
            // 将 duration 写入到txt文件中
            let mut file = OpenOptions::new()
                .create(true) // 如果文件不存在则创建
                .append(true) // 不以追加模式打开
                .open(file_name)
                .expect("无法打开文件");
            writeln!(file, "FRAME_INDEX: {}, EXEC_TIME: {} ms",self.current_frame(), duration_ms).expect("写入文件失败");
            if self.current_frame() != 1000 {
                avg_ex_time += duration_ms;
            }
            else {
                avg_ex_time /= 1000;
                writeln!(file, "AVG_EXEC_TIME: {} ms", avg_ex_time).expect("写入文件失败");
            }

            // FIXME: Should transfer the cmds for a while.
            // FIXME: should remove conflict cmds
            // TODO: ScheCmd has memlimit
            for sche in sches.iter() {
                self.schedule_reqfn_on_node(&mut self.request_mut(sche.reqid), sche.fnid, sche.nid);
            }
            for down in downs.iter() {
                //更新cache
                self.node_mut(down.nid)
                    .try_unload_container(down.fnid, self);
            }
            for up in ups.iter() {
                self.node_mut(up.nid).try_load_container(up.fnid, self);
            }

            self.sim_run();

            self.on_frame_end();

            // // 测试每个函数共有多少容器
            // let mut fn_container_cnt: BTreeMap<FnId, usize> = BTreeMap::new();
            // for func in self.core.fns().iter() {
            //     fn_container_cnt.insert(
            //         func.fn_id,
            //         self.nodes()
            //            .iter()
            //            .filter(|n| n.container(func.fn_id).is_some())
            //            .count(),
            //     );
            // }
            // for (fnid, cnt) in fn_container_cnt.iter() {
            //     log::info!("fn {} , containers {}", fnid, cnt);
            // }

            if self.current_frame() > 1000 {
                self.help.metric_record_mut().flush(self);
                self.reset();
                break;
            }
        }

        // state should has prompt info for next action
        (0.0, "no action".to_string())
    }
}
