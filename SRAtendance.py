# __author__ = 'kevin'
# -*- coding: UTF-8 -*-
from flask import Flask
from flask.ext import restful
import App

app = Flask(__name__)
api = restful.Api(app)

class HelloWorld(restful.Resource):
    def get(self):
        return {'hello': 'world'}
# 根据工号查询个人考勤详情
class Rreport(restful.Resource):
    def get(self,wid):
        work=App.AtendanceWork();
        events=work.queryEventByEm(wid)
        ot_total=work.queryOTByEm(wid)
        detail=work.queryDetailByEm(wid);
        res={}
        res["events"]=events
        res['ot']=ot_total
        res['detail']=detail
        return res

api.add_resource(HelloWorld, '/')
api.add_resource(Rreport,'/report/<string:wid>')
if __name__ == '__main__':
    app.run(debug=True)
