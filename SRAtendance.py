# __author__ = 'kevin'
# -*- coding: UTF-8 -*-
from flask import Flask, jsonify,request
from flask.ext import restful
import App

app = Flask(__name__)
# api = restful.Api(app)
#
# class HelloWorld(restful.Resource):
#     def get(self):
#         return {'hello': 'world'}
# # 根据工号查询个人考勤详情
# class Rreport(restful.Resource):
#     def get(self,wid):
#         work=App.AtendanceWork();
#         events=work.queryEventByEm(wid)
#         ot_total=work.queryOTByEm(wid)
#         detail=work.queryDetailByEm(wid);
#         res={}
#         res["events"]=events
#         res['ot']=ot_total
#         res['detail']=detail
#         return res
# # 根据工号设置是否弹性考核的熟悉
# class EmployeeManage(restful.Resource):
#     def get(self,wid):
#         work=App.AtendanceWork();
#         work.addFlexEmp(wid)
#
#         return None;
#
# # 重新计算考勤
# class Calculate(restful.Resource):
#     def get(self,hour,minute):
#         work=App.AtendanceWork();
#         work.calculate(hour,minute)
#         return None;
#
# api.add_resource(HelloWorld, '/')
# api.add_resource(EmployeeManage, '/config/<string:wid>')
# api.add_resource(Rreport,'/report/<string:wid>')

@app.route('/')
def Hello():
    return 'Hello,welcome'


# 根据工号查询个人考勤详情
@app.route('/report/<string:wid>', methods=['GET'])
def report(wid):
    work = App.AtendanceWork();
    events = work.queryEventByEm(wid)
    ot_total = work.queryOTByEm(wid)
    detail = work.queryDetailByEm(wid);
    res = {}
    res["events"] = events
    res['ot'] = ot_total
    res['detail'] = detail
    return jsonify(res)


# 根据工号设置弹性考核的属性
@app.route('/config/<string:wid>', methods=['UPDATE','DELETE'])
def employeeManage(wid):
    work = App.AtendanceWork();
    if request.method == 'DELETE':
        work.delFlexEmp(wid)
    else:
        work.addFlexEmp(wid)
    return 'success'



# 重新计算考勤
@app.route('/calc/<int:hour>/<int:minute>', methods=['GET'])
def calculate(hour, minute):
    work = App.AtendanceWork();
    work.calculate(hour, minute);
    return 'success'

@app.route('/employee/',methods=['GET'])
def queryFlexEmployee():
    work=App.AtendanceWork();
    res=work.queryFlexEmployee();
    return jsonify(res)

if __name__ == '__main__':
    app.run(debug=True)
