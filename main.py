# coding=utf-8

#
# Copyright 2016 kevin leng
# 处理弹性上班程序
# 1、文件导入考勤记录
# 2、指定早上弹性的时间点，算出迟到的、早退的 员工
# {uid:{date:[start,end],date:[start,end]}}
# 3、展示迟到、早退的员工

from openpyxl import load_workbook
from datetime import *
import calendar
from dateutil.rrule import *
from dateutil.parser import parse
import sys

reload(sys)
sys.setdefaultencoding('utf8')  # 否则打印编码不识别ascii码


class workers:
    def __init__(self):
        pass

    def loaddata(self, filePath):
        wb = load_workbook(filename=filePath, read_only=True)
        # print(wb.get_sheet_names())
        ws = wb['Sheet1']  # ws is now an IterableWorksheet

        user_dic = {}
        u_time = {}
        time = []
        uid = ""
        for row in ws.rows:
            # print(row[2].value)
            user_dic[row[2].value] = row[1].value
            if row[2].value != uid:
                uid = row[2].value
                time = []
            time.append(row[3].value)
            u_time[uid] = time

        # print u_time
        alluser = {}
        for k in u_time.iterkeys():
            # print u'%s:%s'%(k , u_time[k])
            # print k
            if k is None:
                break
            date = ""
            times = []
            dtimes = {}
            start_time = ""
            end_time = ""
            alltimes = []
            for ut in u_time[k]:
                # print ut
                if ut is None or len(ut.split(" ")) < 2:
                    break
                if ut is not None and ut.split(" ")[0] != date:
                    # if dtimes:
                    # 	alltimes.append(dtimes)
                    times = []
                # dtimes={}
                if len(times) > 1:
                    times.pop()
                # times.append(ut.split(" ")[1])
                times.append(ut)
                date = ut.split(" ")[0]
                datek = parse(date).strftime('%Y-%m-%d')
                # tmp=[]
                # tmp.append(times[0])
                # tmp.append(times[len(times)-1])
                dtimes[datek] = times
            # print dtimes
            # print times
            if dtimes:
                alluser[k] = dtimes
            # break
        # print alluser
        return alluser

    # times=[u'2015-12-1 8:58:02', u'2015-12-1 21:46:55']
    def calculate(self, times, start_time, workday):
        msg = ""
        # for workday in wtdata.iterkeys():
        # print workday
        # msg= workday+ " :"
        # times=wtdata[workday]
        # noon = datetime.datetime.strptime(workday+" 12:00:00","%Y-%m-%d %H:%M:%S") #中午分界线
        # start=datetime.datetime.strptime(workday+" "+start_time,"%Y-%m-%d %H:%M") #上班时间 制度

        noon = workday.replace(hour=12);  # 中午分界线
        start = workday.replace(hour=int(start_time.split(":")[0]));  # 上班时间 制度
        start = start.replace(minute=int(start_time.split(":")[1]))
        end = start + timedelta(hours=9)  # 下班时间 制度
        if times is None:
            if workday.weekday() != 5 and workday.weekday() != 6:  # 非周六日
                msg = msg + '缺勤'
            else:
                pass
        elif len(times) == 1:
            # time = TIMEFORMAT(times[0])
            # noon = TIMEFORMAT(workday+" 13:00:00")
            t = datetime.strptime(times[0], "%Y-%m-%d %H:%M:%S")

            # print times[0]
            # print noon

            # print time.mktime(t)  < time.mktime(noon)
            if workday.weekday() != 5 and workday.weekday() != 6:  # 非周六日:
                if t < noon:
                    msg = msg + '下班未打卡-'
                else:
                    msg = msg + '上班未打卡-'
        # print times
        else:
            t1 = datetime.strptime(times[0], "%Y-%m-%d %H:%M:%S")  # 上班时间 实际
            t2 = datetime.strptime(times[1], "%Y-%m-%d %H:%M:%S")  # 下班时间 实际
            wt = (t2 - t1).seconds / 3600
            # print start.ctime();
            # print end.ctime();
            if workday.weekday() != 5 and workday.weekday() != 6:  # 非周六日
                # 是否迟到
                if t1 > start and wt < 8:
                    if t1 > noon:
                        msg = msg + "上班未打卡-"
                    else:
                        msg = msg + "迟到----"

                # 是否早退
                if t2 < end and wt < 8:
                    if t2 < noon:
                        msg = msg + "下班未打卡-"
                    else:
                        msg = msg + "早退----"
                # 是否加班
                if t2 > end and wt >= 8:
                    ot = t2 - end
                    msg = msg + "加班：" + str(round((float(ot.seconds) / 3600), 1)) + " 小时"
            else:
                ot = wt
                msg = msg + "周末加班：" + str(ot) + " 小时"
        if times is None:
            return msg
        else:
            return msg + " 打卡详情： " + ' 至 '.join(times)

    # 获取当月最大天数
    def getWeekday(self, curDay):
        # curMonth : 2015-12-23
        current = parse(curDay)
        cur_year = current.year
        cur_month = current.month
        weekDayNum = calendar.monthrange(cur_year, cur_month)[1]

        weekDays = list(rrule(DAILY, dtstart=parse(str(cur_year) + '-' + str(cur_month) + '-' + '01'),
                              until=parse(str(cur_year) + '-' + str(cur_month) + '-' + str(weekDayNum))));
        return weekDays


if __name__ == "__main__":
    worker = workers()
    data = worker.loaddata("record.xlsm")
    # print data

    for u in data.iterkeys():
        print u
        msg = ""

        weekDays = worker.getWeekday("2015-12-01")
        udata = data.get(u)
        for d in weekDays:
            d_str = d.strftime('%Y-%m-%d')
            times = udata.get(d_str)
            # if times is not None:
            # print times

            res = worker.calculate(times, "9:00", d)
            # if res =="":
            # res="正常"
            msg = msg + d_str + " 周" + str(d.weekday() + 1) + " :" + res + " \n"
            pass
        # elif:
        # 	msg=msg+d+" :缺勤  \n"
        # if data[d]:
        # 	print data[d]
        print msg
		






 
