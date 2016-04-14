DROP TABLE IF EXISTS employee;
CREATE TABLE employee (
  id    SERIAL,
  wid   VARCHAR(20),
  name  VARCHAR(40),
  dep   VARCHAR(100),
  bakup VARCHAR(400),
  PRIMARY KEY (id),
  CONSTRAINT un_key UNIQUE (wid)
);
DROP TABLE IF EXISTS atendance;
CREATE TABLE atendance (
  id    SERIAL,
  wid   VARCHAR(20),
  adate DATE,
  atime TIME,
  PRIMARY KEY (id)
);
DROP TABLE IF EXISTS report;
CREATE TABLE report (
  id           SERIAL,
  wid          VARCHAR(20),
  workDate     DATE,
  firstAt      TIME,
  sedAt        TIME,
  wt           INTERVAL,
  isLate       BOOLEAN,
  isLeaveEarly BOOLEAN,
  missMor       BOOLEAN,
  missNoon       BOOLEAN,
  ot          INTERVAL,
  PRIMARY KEY (id)
);
-- 查询每日打卡最早和最晚的记录
-- select wid ,adate,min(atime) as mintime,max(atime) as maxtime from atendance m  group by wid,adate order by wid,adate;
-- wt
-- update report set wt = justify_hours(sedat-firstat);
-- ot
-- update report set  ot=(wt - interval '8:00')  where (wt - interval '8:00') > interval '00' ;
--迟到 9 变量
-- update report set islate = true where firstat > time '9:00' and wt <> interval '00:00' and firstat < time '12:00';
-- 早退 18 变量
-- update report set isLeaveEarly = true where  wt <> interval '00:00' and sedAt < time '18:00' and sedAt > time '12:00';
--早上未打卡
-- update report set missMor = true  where firstat > time '12:00' ;
--下午未打卡
-- update report set missNoon = true  where sedAt  < time '12:00' ;

-- 统计加班 个人
-- select sum(ot) from report where wid = 'SR000020';
-- 统计个人情况

-- select count(islate) as late ,count(isleaveearly) as ear ,count(missmor), count(missnoon),count(ot) from report where wid = 'SR000020';