# __author__ = 'kevin'
# -*- coding: UTF-8 -*-
import os
from flask import Flask, jsonify, request, render_template
import sys
import App

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/config/')
def admin():
    return render_template('Admin.html')


@app.route('/report/')
def reporthtml():
    return render_template('inquiry.html')


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
@app.route('/config/<string:wid>', methods=['UPDATE', 'DELETE'])
def employeeManage(wid):
    work = App.AtendanceWork();
    if request.method == 'DELETE':
        work.delFlexEmp(wid)
    else:
        work.addFlexEmp(wid)
    return 'success'


# 重新计算考勤
@app.route('/calc/<int:hour>/<int:minute>', methods=['UPDATE','GET'])
def calculate(hour, minute):
    work = App.AtendanceWork();
    work.calculate(hour, minute);
    return 'Success'


# 获取弹性考核的员工
@app.route('/employee/', methods=['GET'])
def queryFlexEmployee():
    work = App.AtendanceWork();
    res = work.queryFlexEmployee();
    return jsonify(res)


# 获取所有的员工
@app.route('/employees/<name>', methods=['GET'])
def queryAllEmployee(name):
    work = App.AtendanceWork();
    res={}
    res['ems'] = work.queryAllEmployee(name);

    return jsonify(res)


# 文件上传并解析入库
@app.route('/file/', methods=['POST', 'GET'])
def fileUpload():
    if request.method == 'POST':
        f = request.files['file']
        path = os.path.join(os.path.dirname(__file__), "file/" + f.filename)
        f.save(path)
        app = App.AtendanceWork()
        app.extract(path)

        return '上传成功'
    elif request.method == 'GET':
        return render_template('loading.html')


if __name__ == '__main__':
    app.run(debug=True)
