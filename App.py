# __author__ = 'kevin'
# -*- coding: UTF-8 -*-

import pandas as pd
import numpy as np
import sys
import psycopg2 as pg
from datetime import *

reload(sys)
sys.setdefaultencoding('utf-8')


class AtendanceWork:
    def __init__(self):
        pass

    # 读取excel
    def loaddata(self, filePath):
        df = pd.read_excel(filePath)
        # print(type(df))

        return df

    def extract(self, filePath):
        data = self.loaddata(filePath)
        # 连接数据库
        try:
            conn = pg.connect(dbname='atendance', host='10.168.190.191', user='test', password='test', port='5432')
            cur = conn.cursor()
        except Exception, e:
            print "Error: " + e.args[0]

        for row in data.itertuples():
            # print(row[4].split(" ")[0])
            cur.execute("insert into atendance (wid,adate,atime) VALUES (%s,%s,%s)",
                        (row[3], row[4].split(" ")[0], row[4].split(" ")[1]))

        conn.commit()

        allWorks = data.drop_duplicates(data.keys()[2])
        for row in allWorks.itertuples():
            cur.execute("insert into employee (wid,name,dep,bakup) VALUES (%s,%s,%s,%s)",
                        (row[3], row[2], row[1], row[7]));
        conn.commit();

        cur.execute(
            "select wid ,adate,min(atime) as mintime,max(atime) as maxtime from atendance m  group by wid,adate order by wid,adate;")
        rows = cur.fetchall()

        for r in rows:
            cur.execute("insert INTO report (wid,workDate,firstAt,sedAt) VALUES (%s,%s,%s,%s)",
                        (r[0], r[1], r[2], r[3]))
        cur.execute("update report set wt = justify_hours(sedat-firstat);")
        cur.execute("update report set  ot = (wt - interval '8:00')  where (wt - interval '8:00') > interval '00' ;")

        conn.commit()

        cur.close()
        conn.close()

    # 代入上班时间计算
    def calculate(self, hour, minute):
        # 连接数据库
        try:
            conn = pg.connect(dbname='atendance', host='10.168.190.191', user='test', password='test', port='5432')
            cur = conn.cursor()
        except Exception, e:
            print "Error: " + e.args[0]


        # --迟到 9 变量
        # -- update report set islate = true where firstat > time '9:00' and wt <> interval '00:00' and firstat < time '12:00';
        dt = datetime.now()
        # 弹性的 （弹性人员先清空再计算）
        cur.execute("update report set  islate = NULL ,isLeaveEarly= NULL  ,missMor = NULL ,missNoon = NULL ;")
        cur.execute(
            "update report set islate = true where firstat > %s  and wt <> interval '00:00' and firstat < time '12:00' and wid in (SELECT  e.wid from employee e where e.flex = true);",
            (time(hour, minute, 0),))
        # 正常的 以9点
        cur.execute(
            "update report set islate = true where firstat > %s  and wt <> interval '00:00' and firstat < time '12:00' and wid in (SELECT  e.wid from employee e where e.flex is null);",
            (time(9, 0, 0),))
        # -- 早退 18 变量
        # -- update report set isLeaveEarly = true where  wt <> interval '00:00' and sedAt < time '18:00' and sedAt > time '12:00';
        # 弹性的
        cur.execute(
            "update report set isLeaveEarly = true where  wt <> interval '00:00' and sedAt < time %s + interval '8 hours' and sedAt > time '12:00'  and wid in (SELECT  e.wid from employee e where e.flex = true);",
            (time(hour, minute, 0),))
        # 正常的
        cur.execute(
            "update report set isLeaveEarly = true where  wt <> interval '00:00' and sedAt < time %s + interval '8 hours' and sedAt > time '12:00'  and wid in (SELECT  e.wid from employee e where e.flex is null);",
            (time(9, 0, 0),))
        # --早上未打卡
        # -- update report set missMor = true  where firstat > time '12:00' ;
        cur.execute("update report set missMor = true  where firstat > time '12:00' ;")
        # --下午未打卡
        # -- update report set missNoon = true  where sedAt  < time '12:00' ;
        cur.execute("update report set missNoon = true  where sedAt  < time '12:00' ;")

        conn.commit()

        cur.close()
        conn.close()

        return None

    # 设置弹性考核员工
    def addFlexEmp(self, wids):
        # 连接数据库
        try:
            conn = pg.connect(dbname='atendance', host='10.168.190.191', user='test', password='test', port='5432')
            cur = conn.cursor()
        except Exception, e:
            print "Error: " + e.args[0]

        cur.execute("update employee set flex = TRUE WHERE  wid in (%s)", (wids,))
        conn.commit()

        cur.close()
        conn.close()
        return None

    # 取消设置弹性考核员工
    def delFlexEmp(self, wids):
        # 连接数据库
        try:
            conn = pg.connect(dbname='atendance', host='10.168.190.191', user='test', password='test', port='5432')
            cur = conn.cursor()
        except Exception, e:
            print "Error: " + e.args[0]

        cur.execute("update employee set flex = NULL WHERE  wid in (%s)", (wids,))
        conn.commit()

        cur.close()
        conn.close()
        return None

    # 统计加班次数
    def queryOTByEm(self, wid):
        # 连接数据库
        try:
            conn = pg.connect(dbname='atendance', host='10.168.190.191', user='test', password='test', port='5432')
            cur = conn.cursor()
        except Exception, e:
            print "Error: " + e.args[0]

        cur.execute("select sum(ot) from report where wid = %s ", (wid,))
        # cur.fetchall();
        res = {}
        for r in cur.fetchall():
            # print(r[0].total_seconds()/3600)
            # print(str(r[0]))
            # res['加班时间（小时）'] = round(r[0].total_seconds() / 3600, 2);
            res['ot'] = round(r[0].total_seconds() / 3600, 2);
        # conn.commit()

        cur.close()
        conn.close()
        # print(res)
        return res

    # 统计各类事件次数
    def queryEventByEm(self, wid):
        # 连接数据库
        try:
            conn = pg.connect(dbname='atendance', host='10.168.190.191', user='test', password='test', port='5432')
            cur = conn.cursor()
        except Exception, e:
            print "Error: " + e.args[0]

        cur.execute(
            "select count(islate),count(isleaveearly),count(missmor),count(missnoon),count(ot) from report where wid = %s ",
            (wid,))
        res = {}
        for r in cur.fetchall():
            # res['迟到'] = r[0]
            # res['早退'] = r[1]
            # res['早上未打卡'] = r[2]
            # res['下午未打卡'] = r[3]
            # res['加班'] = r[4]
            res['late'] = r[0]
            res['early_exit'] = r[1]
            res['no_clock_in_am'] = r[2]
            res['no_clock_in_pm'] = r[3]
            res['ot'] = r[4]
            # print(r[0])
        # conn.commit()

        cur.close()
        conn.close()
        # print(res)
        return res

    # 查询考勤详情
    def queryDetailByEm(self, wid):
        # 连接数据库
        try:
            conn = pg.connect(dbname='atendance', host='10.168.190.191', user='test', password='test', port='5432')
            cur = conn.cursor()
        except Exception, e:
            print "Error: " + e.args[0]

        cur.execute("select * from report where wid = %s  ORDER BY workdate", (wid,))
        res = []
        for r in cur.fetchall():
            row = {};
            row['wid'] = r[1]
            # row['weekday']=r[2].weekday()
            # row['date'] = r[2].strftime("%A %y-%m-%d")
            row['date'] = r[2].strftime("%Y-%m-%d")
            row['first'] = r[3].strftime("%H:%M:%S %Z")
            row['second'] = r[4].strftime("%H:%M:%S %Z")
            row['late'] = r[6]
            row['earlyout'] = r[7]
            row['mismor'] = r[8]
            row['misnoon'] = r[9]
            row['ot'] = str(r[10])
            res.append(row);

        # conn.commit()

        cur.close()
        conn.close()
        return res
    # 查询弹性考核的员工
    def queryFlexEmployee(self):
        # 连接数据库
        try:
            conn = pg.connect(dbname='atendance', host='10.168.190.191', user='test', password='test', port='5432')
            cur = conn.cursor()
        except Exception, e:
            print "Error: " + e.args[0]

        cur.execute("select name,wid from employee where flex = TRUE  ORDER BY wid")
        # row = {};
        # for r in cur.fetchall():
        #     row[r[0]]=r[1]
        return cur.fetchall()
        # return row


if __name__ == "__main__":
    work = AtendanceWork();
    em = ('SR000118', 'SR000123')
    # work.extract("file/test.xlsx")
    work.addFlexEmp(em)
    work.calculate(9, 0);
    # work.queryDetailByEm("SR000020");