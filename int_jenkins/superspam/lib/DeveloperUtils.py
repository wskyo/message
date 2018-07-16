#!/usr/bin/env python
# -*- coding: utf-8 -*-

#--------engnieer info--------------------------
leaderList = [
        'shie.zhao@tcl.com',
        'xiaofen.zhong@tcl.com',
        'zhiquan.wen.hz@tcl.com',
        'zongmin.lu@tcl.com',
        'hanwu.xie@tcl.com',
        'zhixiong.liu.hz@tcl.com',
        'yunqing.huang@tcl.com',
        'haihui.jiang.hz@tcl.com',
]

project_managers = [
        'wenfeng.wu@tcl.com',
        'jinhan.li@tcl.com',
        'yuanpeng.liu@tcl.com',      
        ]

app = [
        'zhibin.zhong@tcl.com',
        'ligang.nie@tcl.com',
        'jian.guan.hz@tcl.com',
        'mingjun.yong@tcl.com',
        'guoqiang.tan.hz@tcl.com',
        'manbiao.wang.hz@tcl.com',
        'shilei.zhang@tcl.com',
        'weiwen.huang.hz@tcl.com',
        'tao.luo@tcl.com',
        'dongbo.shao.hz@tcl.com', 
        'yidan.qu.hz@tcl.com',
        'huawei.wang@tcl.com',
        'bin.wu@tcl.com',
        'wweixiong@tcl.com',
        ]

Tel = [
        'donghai.wu@tcl.com',
        'kai.wang.hz@tcl.com',
        'minguo.wan@tcl.com',
        'jianping.zhang@tcl.com',
        'yong.wei@tcl.com',
        'wei.wang.hz@tcl.com',
        'shengjiao.liu.hz@tcl.com',
        'chenli.gao.hz@tcl.com',
        'chengjun.hu.hz@tcl.com',
        'zubin.chen.hz@tcl.com',
        'kaishu.li.hz@tcl.com',
        'yong.zhang.hz@tcl.com',
        'zhiyuan.li@tcl.com',
        'yangning.hong@tcl.com',
        'yaodong.shen@tcl.com',
       ]

Sys = [
        'zeming.huang@tcl.com',
        'jinguo.zheng@tcl.com',
        'zhongyang.hu@tcl.com',
        'yuepeng.li@tcl.com',
        'yan.he.hz@tcl.com',
        'yiping.wang@tcl.com',
        'guofei.xie.hz@tcl.com',
        'yisen.tang.hz@tcl.com',
        'guangxi.deng.hz@tcl.com',
        'jinlong.sang.hz@tcl.com',
        'yan.fang@tcl.com',
        'haibo.zhong.hz@tcl.com',
          ]

Multi = [
        'qingtao.wen@tcl.com',
        'yuxin.xu@tcl.com',
        'shaohua.liu@tcl.com',
        'jianqing.zeng@tcl.com',
        'wenzhen.miao@tcl.com',
        'kai.zhang.hz@tcl.com',
        'wanlin.qin.hz@tcl.com',
        'xuchao.pang.hz@tcl.com',
        'meiling.zhang.hz@tcl.com',
        'wei.li.hz@tcl.com',
        'yang.sun@tcl.com',
        'lin.long.hz@tcl.com',
        'min.zhang.hz@tcl.com',
        ]

Driverteam = [
        'jie.fang@tcl.com',
        'jingjing.jiang.hz@tcl.com',
        'lianghan.yu.hz@tcl.com',
        'ersen.shang@tcl.com',
        'yaosen.lin@tcl.com',
        'xiaopu.zhu@tcl.com',
        ]

persoteam = [
          'shuang.zhong.hz@tcl.com',
          'yingying.qiao.hz@tcl.com',
          'feng.wang.hz@tcl.com',
          'lei.guo.hz@tcl.com',
          'xiaoling.luo@tcl.com',
          'yanxiang.zhang@tcl.com',
         ]

integration = [
          'xueqin.zhang@tcl.com',
          'yinfang.lai@tcl.com',
          'renzhi.yang.hz@tcl.com',
          'yan.xiong@tcl.com',
          'xiaoli.luo@tcl.com',
         ]

toolsteam = [
          'baoge.li.hz@tcl.com',
          'chaoyang.xue.hz@tcl.com',
          'zhihua.li.hz@tcl.com',
          'yi.xie@tcl.com',
          'zhiqiang.hu@tcl.com',
         ]

SPM = [
          'yaoting.wei@tcl.com',
          'hui.shen@tcl.com',
          'feng.xu@tcl.com',
          'yajiao.wei@tcl.com',     
         ]

#nj_site = [
#           'xiaochuan.zhao@tct-nj.com',
#           'binbin.xu@tct-nj.com',
#           'wei.gao@tct-nj.com',
#           'haidong.wang@tct-nj.com',
#           'jian.liu@tct-nj.com',
#           'ting.zhu@tct-nj.com',
#           'kui.wang@tct-nj.com',
#           'weixing.tian@tct-nj.com',
#           'guoqing.li@tct-nj.com',
#           'xingke.wu@tct-nj.com',
#           'jingjing.zhu@tct-nj.com',
#           'quanshui.ye@tct-nj.com',
#           'jingyang.wang@tct-nj.com',
#           'yongjie.xiao@tct-nj.com',
#           'li.zhao@tct-nj.com',
#           'bin.wang@tct-nj.com',
#           'xinxin.dou@tct-nj.com',
#           'liming.wang@tct-nj.com',
#           'lei.qiu@tct-nj.com',
#           'wentao.wan@tct-nj.com'
#          ]

#sh_site = [
 #          'chuan.wei@tcl.com',
#           'xiaochun.zhang@tct-nj.com',
#           'shengyi.zhang@tcl.com',
#           'jian.bu@tct-nj.com',
#           'songlan.pu@tcl.com',
#           'guoxing.pei@tct-nj.com',
#           'guodong.cao@tcl.com',
#           'xiange.hu@tcl.com',
#           'xifeng.guo@tcl.com',
#           'jia.liu@tct-nj.com',
#           'hongwu.he@tcl.com',
#           'songzhen.zhang@tcl.com',
#           'jing.sha@tcl.com',
 #          'jianzhi.qiu@tct-nj.com',
#           'jin.zhang2@tct-nj.com',
 #          'rengcang.liu@tcl.com',
#           'yuming.mao@tct-nj.com',
#           'xiaohui.liu@tcl.com',
 #          'bin.hui@tct-nj.com',
#           'alan.liu@tcl.com',
  #         'zhongwen.yu@tcl.com',
#           'da.zheng@tcl.com',
  #         'dan.han@tcl.com',
#           'cai.jin@tcl.com',
  #         'feng.wang@tcl.com',
   #        'jie.li@tcl.com',
  #         'jingang.yi@tcl.com',
   #        'qiujing.ren@tcl.com',
   #        'yanlong.li@tcl.com',
   #        'zhengyong.wang@tcl.com',
  #         'zhonglei.lv@tcl.com',
  #         'jinfeng.ye.hz@tcl.com',
  #         'zongmin.ye@tcl.com',
  #         'john.sun@tcl.com',
  #         'hong.duan@tct-nj.com',
  #         'gaoxiang.li.hz@tcl.com',
   #        'jeff.wang@tcl.com',
  #         'longbin.wu@tct-nj.com',
  #        ]
engineer = app + Tel + Sys + Multi + Driverteam + toolsteam + persoteam+ integration + SPM + project_managers+leaderList

