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
        data = work.loaddata(filePath)
        # 连接数据库
        try:
            conn = pg.connect(dbname='atendance', host='127.0.0.1', user='test', password='test', port='5432')
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

    def calculate(self, starttime):
        # 连接数据库
        try:
            conn = pg.connect(dbname='atendance', host='127.0.0.1', user='test', password='test', port='5432')
            cur = conn.cursor()
        except Exception, e:
            print "Error: " + e.args[0]

        print(starttime )

        # --迟到 9 变量
        # -- update report set islate = true where firstat > time '9:00' and wt <> interval '00:00' and firstat < time '12:00';
        cur.execute("update report set islate = true where firstat >  time %s and wt <> interval '00:00' and firstat < time '12:00';",("9:00"))
        # -- 早退 18 变量
        # -- update report set isLeaveEarly = true where  wt <> interval '00:00' and sedAt < time '18:00' and sedAt > time '12:00';
        cur.execute("update report set isLeaveEarly = true where  wt <> interval '00:00' and sedAt < time %s + interval '8 hours' and sedAt > time '12:00';",(starttime))
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


if __name__ == "__main__":
    work = AtendanceWork();
    # work.extract("file/test.xlsx")
    work.calculate(9)
