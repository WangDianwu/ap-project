import string

import hashlib

# excel操作
import xlrd as xlrd
from flask import Flask, redirect, url_for, request, Response, render_template, flash, session
# 数据库操作
import sqlite3
from database.helper.sqlithelper import *



app = Flask(__name__,
template_folder='web/page',
static_folder='web/assets')
# 指定了模板加载位置和静态文件加载位置


app.secret_key = "jJInfewp(8efkd*9&jfkl"      # flash的消息都存储在session，需要一个会话密匙，密匙随便输入就行，如果对保密性要求高的话，可以使用相关的密匙生成函数，不在细讲

# 初始化路由匹配/   默认页
@app.route('/')
def index():
    session.clear()
    return render_template('login.html')

#  登录方法
@app.route('/login', methods=['POST', 'GET'])   #登录信息处理界面，处理由'/'传送过来的表单信息
def result():
    #如果使用post方法传送过来的数据才验证
    
    if request.method == 'POST':
        #获取表单数据
        username = request.form.get('username')
        password = request.form.get('password')
        usertype = request.form.get('usertype')
        #从数据库中验证信息是否正确
        # 创建md5对象
        m = hashlib.md5()
        b = password.encode(encoding='utf-8')
        m.update(b)
        password_md5 = m.hexdigest()
        name = ''
        # 学生
        if usertype == 'student':
            result, _ = GetSql2("select name from student where num = '"+username+"' and password = '"+password+"'")
            name = result[0][0]
        # 教师
        if usertype == 'teacher':
            result, _ = GetSql2("select 姓名 from teacher where 编号 = '"+username+"' and 密码 = '"+password+"'")
            name = result[0][0]
        # admin  默认走管理员方式 
        if username == 'admin':
            result, _ = GetSql2("select * from sys_user where username = '"+username+"' and userpwd = '"+password_md5+"'")
        if result: #登录成功，页面跳转到相应的功能页面
            # return '登录成功'
            if username == 'admin':
                return render_template("manager.html", name=username)
            if usertype == 'teacher':
                return render_template("teacher.html", name=name, bianhao=username)
            if usertype == 'student':
                return render_template("student.html", name=name, xuehao=username)
        else:
            flash("您输入的用户名和密码有误，请重新输入！")
            return redirect(url_for('index'))  # 密码错误重定向到登录页面

    else:
        return redirect(url_for('index'))

# @app.route('/feng')
# def feng():
#    return render_template('fengmian.html')

#个人中心
@app.route('/self_info', methods=["GET"])
def self_info():
    shenfen = request.args.get('shenfen')
    if shenfen == '学生':
        xuehao = request.args.get('xuehao')
        result, _ = GetSql2("select num,name,sex,birthday,sdept.名称,class.名称 from student,sdept,class where student.classnum = class.班级号 and speciality = sdept.编号 and num = '" + xuehao + "'")
        return render_template("student_self.html", student = result[0])
    if shenfen == '教师':
        bianhao = request.args.get('bianhao')
        result, _ = GetSql2("select teacher.编号, 姓名, 性别, 名称, 职称 from teacher, xisuo where teacher.所属系所 = xisuo.编号 and teacher.编号 = '" + bianhao + "'")
        return render_template("teacher_self.html", teacher=result[0])

#点击修改密码，将信息传递到修改密码界面
@app.route('/mima', methods=["GET"])
def password():
    shenfen = request.args.get('shenfen')
    if shenfen == '学生':
        xuehao = request.args.get('xuehao')
        return render_template("mima.html", shenfen=shenfen, hao=xuehao)
    if shenfen == '教师':
        bianhao = request.args.get('bianhao')
        return render_template("mima.html", shenfen=shenfen, hao=bianhao)

#点击修改按钮，修改表中信息
@app.route('/update_mima', methods=['POST'])
def update_password():
    result = ""
    shenfen = request.form.get('shenfen')
    hao = request.form.get('hao')
    mima = request.form.get('mima')
    if shenfen == '学生':
        data = dict(num = hao, password = mima)
        result = UpdateData(data, "student")
        return render_template("mima.html", shenfen=shenfen, hao=hao, result=result)
    if shenfen == '教师':
        data = dict(编号 = hao, 密码 = mima)
        result = UpdateData(data, "teacher")
        return render_template("mima.html", shenfen=shenfen, hao=hao, result=result)

#必修
@app.route('/bixiu', methods=["GET"])
def into_bixiu():
    xuehao = request.args.get('xuehao')
    page = int(request.args.get('page', 1)) #默认值为1
    alert = request.args.get('result', '') #默认值为空
    if page <= 0:
        page = 1
    #设置每一页展示5行
    hang = 5
    #查询未选的必修课，获取页数
    result, _ = GetSql2("select count(*) from course,tea_cou where course.课程编号 = tea_cou.课程编号 and 课程类别 = '必修' and tea_cou.课程编号 not in (select 课程编号 from stu_cou where 学号 = '"+xuehao+"')")
    result_num = result[0][0]
    page_num = int(int(result_num) / hang)
    if result_num % hang != 0:
        page_num = page_num + 1
    #计算当前页数，查询该范围内的必修课
    current_page = page
    start_hang = (page - 1) * hang
    result, _ = GetSql2("select * from bixiu where 课程编号 not in (select 课程编号 from stu_cou where 学号 = '"+xuehao+"') limit "+str(hang)+" offset "+str(start_hang)+"")
    #根据result中的课程编号，获取开课班级
    for i in range(len(result)):
        sql = "select 名称 from open_cou, class where class.班级号 = open_cou.班级号 and 课程编号 = '"+result[i][0]+"'"
        r1, _ = GetSql2(sql)
        result[i] = (result[i], r1)
    #获取剩余人数
    return render_template("bixiu.html", xuehao=xuehao, results=result, page_num=page_num, current_page=current_page, result_num = result_num, result = alert)

#选课
@app.route('/xuanke', methods=['POST', 'GET'])
def sel_cou():
    if request.method == 'POST':
        #证明是form的整体提交，是批量选课
        #获取学号和批量课号和课序号
        xuehao = request.form.get('xuehao')
        couids = request.form.getlist('couid')
        #couid是列表的形式，['12301+1', '12302+1']，用字典的方式获取数据
        ke = []
        for couid in couids:
            index = couid.find('+')
            dic = {}
            dic['kehao'] = couid[:index]
            dic['kexuhao'] = couid[index+1:]
            ke.append(dic)
        #调用插入函数
        flag = 0
        error = []
        for k in ke:
            data = dict(学号 = xuehao, 课程编号 = k['kehao'], 课序号 = k['kexuhao'])
            result = InsertData(data, "stu_cou")
            if result == '选课成功':
                continue
            else:
                flag = 1
                error.append(k)
        if flag == 1:
            result = "您选择的"
            for e in error:
                result = result+"课程编号为{}、课序号为{}的课,".format(e['kehao'], e['kexuhao'])
            result = result + "选课失败！！"

        return redirect(url_for('into_bixiu', xuehao=xuehao, result=result))
    else:
        #证明是单独的选课
        xuehao = request.args.get('xuehao')
        kehao = request.args.get('kehao')
        kexuhao = request.args.get('kexuhao')
        data = dict(学号 = xuehao, 课程编号 = kehao, 课序号 = kexuhao)
        result = InsertData(data, "stu_cou")
        return redirect(url_for('into_bixiu', xuehao=xuehao, result=result))

#通选限选
@app.route('/tongxuan', methods=["GET"])
def into_tongxuan():
    xuehao = request.args.get('xuehao')
    page = int(request.args.get('page', 1))  # 默认值为1
    alert = request.args.get('result', '')  # 默认值为空
    if page <= 0:
        page = 1
    # 设置每一页展示5行
    hang = 5
    # 查询未选的必修课，获取页数
    result, _ = GetSql2("select count(*) from course,tea_cou where course.课程编号 = tea_cou.课程编号 and 课程类别 = '通选限选' and tea_cou.课程编号 not in (select 课程编号 from stu_cou where 学号 = '" + xuehao + "')")
    result_num = result[0][0]
    page_num = int(int(result_num) / hang)
    if result_num % hang != 0:
        page_num = page_num + 1
    # 计算当前页数，查询该范围内的必修课
    current_page = page
    start_hang = (page - 1) * hang
    result, _ = GetSql2("select * from tongxuan where 课程编号 not in (select 课程编号 from stu_cou where 学号 = '" + xuehao + "') limit " + str(hang) + " offset " + str(start_hang) + "")
    # 根据result中的课程编号，获取开课班级
    for i in range(len(result)):
        sql = "select 名称 from open_cou, class where class.班级号 = open_cou.班级号 and 课程编号 = '" + result[i][0] + "'"
        r1, _ = GetSql2(sql)
        result[i] = (result[i], r1)
    # 获取剩余人数
    return render_template("tongxuan.html", xuehao=xuehao, results=result, page_num=page_num, current_page=current_page,
                           result_num=result_num, result=alert)


#专业限选
@app.route('/zhuanye', methods=["GET"])
def into_zhuanye():
    xuehao = request.args.get('xuehao')
    page = int(request.args.get('page', 1))  # 默认值为1
    alert = request.args.get('result', '')  # 默认值为空
    if page <= 0:
        page = 1
    # 设置每一页展示5行
    hang = 5
    # 查询未选的必修课，获取页数
    result, _ = GetSql2("select count(*) from course,tea_cou where course.课程编号 = tea_cou.课程编号 and 课程类别 = '专业限选' and tea_cou.课程编号 not in (select 课程编号 from stu_cou where 学号 = '" + xuehao + "')")
    result_num = result[0][0]
    page_num = int(int(result_num) / hang)
    if result_num % hang != 0:
        page_num = page_num + 1
    # 计算当前页数，查询该范围内的必修课
    current_page = page
    start_hang = (page - 1) * hang
    result, _ = GetSql2("select * from zhuanye where 课程编号 not in (select 课程编号 from stu_cou where 学号 = '" + xuehao + "') limit " + str(hang) + " offset " + str(start_hang) + "")
    # 根据result中的课程编号，获取开课班级
    for i in range(len(result)):
        sql = "select 名称 from open_cou, class where class.班级号 = open_cou.班级号 and 课程编号 = '" + result[i][0] + "'"
        r1, _ = GetSql2(sql)
        result[i] = (result[i], r1)
    # 获取剩余人数
    return render_template("zhuanye.html", xuehao=xuehao, results=result, page_num=page_num, current_page=current_page,
                           result_num=result_num, result=alert)

#进入退课页面
@app.route('/tuike', methods=["GET"])
def into_tuike():
    xuehao = request.args.get('xuehao')
    page = int(request.args.get('page', 1))  # 默认值为1
    alert = request.args.get('result', '')  # 默认值为空
    if page <= 0:
        page = 1
    # 设置每一页展示5行
    hang = 5
    #查询该学生已选的课程
    result, _ = GetSql2("select count(*) from stu_cou where 学号 = '"+xuehao+"'")
    result_num = result[0][0]
    page_num = int(int(result_num) / hang)
    if result_num % hang != 0:
        page_num = page_num + 1
    # 计算当前页数，查询该范围内的必修课
    current_page = page
    start_hang = (page - 1) * hang
    result, _ = GetSql2("select * from yixuan,stu_cou where yixuan.课程编号 = stu_cou.课程编号 and yixuan.课序号 = stu_cou.课序号 and 学号 = '"+xuehao+"' limit " + str(hang) + " offset " + str(start_hang) + "")
    # 根据result中的课程编号，获取开课班级
    for i in range(len(result)):
        sql = "select 名称 from open_cou, class where class.班级号 = open_cou.班级号 and 课程编号 = '" + result[i][0] + "'"
        r1, _ = GetSql2(sql)
        result[i] = (result[i], r1)
    return render_template("tuike.html", xuehao=xuehao, results=result, page_num=page_num, current_page=current_page,
                           result_num=result_num, result=alert)

#退课
@app.route('/tui_cou', methods=['POST', 'GET'])
def tui_cou():
    if request.method == 'POST':
        #证明是form的整体提交，是批量退课
        #获取学号和批量课号和课序号
        xuehao = request.form.get('xuehao')
        couids = request.form.getlist('couid')
        #couid是列表的形式，['12301+1', '12302+1']，用字典的方式获取数据
        ke = []
        for couid in couids:
            index = couid.find('+')
            dic = {}
            dic['kehao'] = couid[:index]
            dic['kexuhao'] = couid[index+1:]
            ke.append(dic)
        #调用删除函数
        flag = 0
        error = []
        for k in ke:
            result = DelDataById("delete from stu_cou where 学号 = '"+xuehao+"' and 课程编号 = '"+k['kehao']+"' and 课序号 = '"+k['kexuhao']+"'")
            if result == '退课成功':
                continue
            else:
                flag = 1
                error.append(k)
        if flag == 1:
            result = "您选择的"
            for e in error:
                result = result+"课程编号为{}、课序号为{}的课,".format(e['kehao'], e['kexuhao'])
            result = result + "退课失败！！"

        return redirect(url_for('into_tuike', xuehao=xuehao, result=result))
    else:
        #证明是单独的退课
        xuehao = request.args.get('xuehao')
        kehao = request.args.get('kehao')
        kexuhao = request.args.get('kexuhao')
        result = DelDataById("delete from stu_cou where 学号 = '"+xuehao+"' and 课程编号 = '"+kehao+"' and 课序号 = '"+kexuhao+"'")
        return redirect(url_for('into_tuike', xuehao=xuehao, result=result))

#学生查询成绩页面
@app.route('/stu_mark', methods=['POST', 'GET'])
def into_stu_mark():
    #根据学号查询出成绩单
    xuehao = request.args.get('xuehao')
    result = request.args.get('result', '')
    pingshi = int(request.args.get('pingshi', 0))
    kaoshi = int(request.args.get('kaoshi', 0))
    sql = "select stu_cou.课程编号, 课序号, 名称, 学分, 课程类别, 平时成绩, 考试成绩 from stu_cou, course where stu_cou.课程编号 = course.课程编号 and 学号 = '"+xuehao+"' and 平时成绩 != 0 and 考试成绩!=0"
    r, _ = GetSql2(sql)

    return render_template("stu_cha_mark.html", xuehao=xuehao, results=r, result=result, pingshi=pingshi, kaoshi=kaoshi)

#学生输入课程编号和课序号查询成绩
@app.route('/stu_cha_mark', methods=['POST'])
def stu_cha_mark():
    #接受学号，课程编号，课序号
    xuehao = request.form.get('xuehao')
    kehao = request.form.get('kehao')
    kexuhao = request.form.get('kexuhao')
    #检验是否是该学生所选课程，以及该课程是否已经发布成绩
    result = ""
    r, _ = GetSql2("select * from stu_cou where 学号 = '"+xuehao+"' and 课程编号 = '"+kehao+"' and 课序号 = '"+kexuhao+"' and 平时成绩 != 0 and 考试成绩 != 0")
    if len(r) == 0:
        result = "您未选修该课程或者该课程并未公布成绩！"
        return redirect(url_for('into_stu_mark', xuehao=xuehao, result=result))
    else:
        #获取平时成绩和考试成绩
        pingshi = r[0][3]
        kaoshi = r[0][4]
        return redirect(url_for('into_stu_mark', xuehao=xuehao, pingshi=pingshi, kaoshi=kaoshi))

#教师成绩查询页面
@app.route('/tea_mark', methods=['GET'])
def tea_mark():
    #获取编号
    bianhao = request.args.get('bianhao')
    #查询教师所教授的课程
    result, _ = GetSql2("select tea_cou.课程编号, 课序号, 名称, 学分, 课程类别 from tea_cou, course where tea_cou.课程编号 = course.课程编号 and 任课教师 = '"+bianhao+"'")
    return render_template("tea_cha_mark.html", bianhao=bianhao, results=result)




#教师点击查询
@app.route('/tea_cha', methods=['GET'])
def tea_cha():
    bianhao = request.args.get('bianhao')
    kehao = request.args.get('kehao')
    kexuhao = request.args.get('kexuhao')
    page = int(request.args.get('page', 1))  # 默认值为1
    r = request.args.get('result', '') #默认值设为空
    if page <= 0:
        page = 1
    # 设置每一页展示5行
    hang = 5
    #查询选修这门课程的所有学生
    sql1 = "select count(*) from stu_cou where 课程编号 = '"+kehao+"' and 课序号 = '"+kexuhao+"'"
    result, _ = GetSql2(sql1)
    result_num = result[0][0]
    page_num = int(int(result_num) / hang)
    if result_num % hang != 0:
        page_num = page_num + 1
    # 计算当前页数，查询该范围内的学生
    current_page = page
    start_hang = (page - 1) * hang
    sql = "select stu_cou.学号, name, sex, sdept.名称, class.名称, 平时成绩, 考试成绩 from stu_cou, student, sdept, class where stu_cou.学号 = student.num and sdept.编号 = student.speciality and class.班级号 = student.classnum and 课程编号 = '"+kehao+"' and 课序号 = '"+kexuhao+"' limit " + str(hang) + " offset " + str(start_hang) + ""
    result, _ = GetSql2(sql)
    #计算出总成绩
    #判断平时成绩和考试成绩是否已经公布
    pingshi = ''
    kaoshi = ''
    zong = 0
    for i in range(len(result)):
        if result[i][5] is None:
            pingshi = '未公布'
        if result[i][6] is None:
            kaoshi = '未公布'
        if result[i][5] is not None and result[i][6] is not None:
            zong = int(int(result[i][5]) * 0.3 + int(result[i][6]) * 0.7)
        result[i] = (result[i], zong)

    return render_template("stu_mark.html", bianhao=bianhao, results=result, page_num=page_num, current_page=current_page,
                           result_num=result_num, kehao=kehao, kexuhao=kexuhao, pingshi=pingshi, kaoshi=kaoshi, result=r, zong=zong)

#教师开课信息界面
@app.route('/tea_cou', methods=['GET'])
def tea_cou():
    #获取编号
    bianhao = request.args.get('bianhao')
    #查询教师所教授的课程
    result, _ = GetSql2("select tea_cou.课程编号, 课序号, 名称, 学分, 课程类别, 开课学期, 上课地点, 周数, 星期, 节数 from tea_cou, course where tea_cou.课程编号 = course.课程编号 and 任课教师 = '"+bianhao+"'")
    #查询选择该课程的学生人数
    for i in range(len(result)):
        num, _ = GetSql2("select count(*) from stu_cou where 课程编号 = '"+str(result[i][0])+"' and 课序号 = '"+str(result[i][1])+"'")
        result[i] = (result[i], num[0])

    return render_template("tea_cou.html", bianhao=bianhao, results=result)



#查询选修该课程的学生名单
@app.route('/tea_stu', methods=['GET'])
def tea_stu():
    bianhao = request.args.get('bianhao')
    kehao = request.args.get('kehao')
    kexuhao = request.args.get('kexuhao')
    page = int(request.args.get('page', 1))  # 默认值为1
    if page <= 0:
        page = 1
    # 设置每一页展示5行
    hang = 5
    # 查询选修这门课程的所有学生
    sql1 = "select count(*) from stu_cou where 课程编号 = '" + kehao + "' and 课序号 = '" + kexuhao + "'"
    result, _ = GetSql2(sql1)
    result_num = result[0][0]
    page_num = int(int(result_num) / hang)
    if result_num % hang != 0:
        page_num = page_num + 1
    # 计算当前页数，查询该范围内的学生
    current_page = page
    start_hang = (page - 1) * hang
    sql = "select stu_cou.学号, name, sex, sdept.名称, class.名称 from stu_cou, student, sdept, class where stu_cou.学号 = student.num and sdept.编号 = student.speciality and class.班级号 = student.classnum and 课程编号 = '" + kehao + "' and 课序号 = '" + kexuhao + "' limit " + str(
        hang) + " offset " + str(start_hang) + ""
    result, _ = GetSql2(sql)
    return render_template("tea_stu.html", bianhao=bianhao, results=result, page_num=page_num,
                           current_page=current_page,
                           result_num=result_num, kehao=kehao, kexuhao=kexuhao)

#单个录入学生成绩界面
@app.route('/luru', methods=['GET'])
def luru():
    #获取学生的学号,课程的课程编号和课序号
    xuehao = request.args.get('xuehao')
    kehao = request.args.get('kehao')
    kexuhao = request.args.get('kexuhao')
    bianhao = request.args.get('bianhao')
    page = request.args.get('page')

    return render_template("luru.html", xuehao=xuehao, kehao=kehao, kexuhao=kexuhao, bianhao=bianhao, page=page)

#单个录入学生成绩
@app.route('/luru_mark', methods=['POST'])
def luru_mark():
    xuehao = request.form.get('xuehao')
    kehao = request.form.get('kehao')
    kexuhao = request.form.get('kexuhao')
    pingshi = request.form.get('pingshi')
    kaoshi = request.form.get('kaoshi')
    bianhao = request.form.get('bianhao')
    page = request.form.get('page')
    sql = "update stu_cou set 平时成绩 = "+pingshi+", 考试成绩 = "+kaoshi+" where 学号 = '"+xuehao+"' and 课程编号 = '"+kehao+"' and 课序号 = '"+kexuhao+"'"
    result = UpdateData1(sql)

    return redirect(url_for('tea_cha', bianhao=bianhao, result=result, page=page, kehao=kehao, kexuhao=kexuhao))

#单个修改学生成绩界面
@app.route('/xiugai', methods=['GET'])
def xiugai():
    #获取学生的学号,课程的课程编号和课序号
    xuehao = request.args.get('xuehao')
    kehao = request.args.get('kehao')
    kexuhao = request.args.get('kexuhao')
    bianhao = request.args.get('bianhao')
    page = request.args.get('page')
    #查询平时成绩和考试成绩
    result, _ = GetSql2("select 平时成绩, 考试成绩 from stu_cou where 学号 = '"+xuehao+"' and 课程编号 = '"+kehao+"' and 课序号 = '"+kexuhao+"'")

    return render_template("xiugai.html", xuehao=xuehao, kehao=kehao, kexuhao=kexuhao, bianhao=bianhao, page=page, result=result)


# 单个修改学生成绩
@app.route('/xiugai_mark', methods=['POST'])
def xiugai_mark():
    xuehao = request.form.get('xuehao')
    kehao = request.form.get('kehao')
    kexuhao = request.form.get('kexuhao')
    pingshi = request.form.get('pingshi')
    kaoshi = request.form.get('kaoshi')
    bianhao = request.form.get('bianhao')
    page = request.form.get('page')
    sql = "update stu_cou set 平时成绩 = " + pingshi + ", 考试成绩 = " + kaoshi + " where 学号 = '" + xuehao + "' and 课程编号 = '" + kehao + "' and 课序号 = '" + kexuhao + "'"
    result = UpdateData1(sql)

    return redirect(url_for('tea_cha', bianhao=bianhao, result=result, page=page, kehao=kehao, kexuhao=kexuhao))

#进入Excel文件成绩批量录入界面
@app.route('/excel', methods=['GET'])
def excel():
    #获取编号
    bianhao = request.args.get('bianhao')
    r = request.args.get('result', '')
    #查询教师所教授的课程
    result, _ = GetSql2("select tea_cou.课程编号, 课序号, 名称, 学分, 课程类别 from tea_cou, course where tea_cou.课程编号 = course.课程编号 and 任课教师 = '"+str(bianhao)+"'")
    return render_template("excel.html", bianhao=bianhao, results=result, result=r)

#进入Excel文件成绩批量录入
@app.route('/excel_mark', methods=['POST', 'GET'])
def excel_mark():
    if request.method == 'POST':
        kehao = request.form.get('kehao')
        kexuhao = request.form.get('kexuhao')
        bianhao = request.form.get('bianhao')
        #获取文件
        file = request.files.get('file')
        f = file.read()  #文件内容
        data = xlrd.open_workbook(file_contents=f)
        table = data.sheets()[0]
        nrows = table.nrows  # 获取该sheet中的有效行数
        ncols = table.ncols  # 获取该sheet中的有效列数
        #excel文件的内容格式必须是学号，平时成绩，考试成绩
        list = []
        for i in range(nrows):
            rowlist = []
            for j in range(ncols):
                rowlist.append(table.cell_value(i, j))
            list.append(rowlist)
        del list[0]  # 删掉第一行，第一行获取的是文件的头
        #将数据存储到数据库中
        result = ''
        flag = 0
        for a in list:
            sql = "update stu_cou set 平时成绩 = " + str(a[1]) + ", 考试成绩 = " + str(a[2]) + " where 学号 = '" + str(a[0]) + "' and 课程编号 = '" + str(kehao) + "' and 课序号 = '" + str(kexuhao) + "'"
            r = UpdateData1(sql)
            if r == '成绩录入成功':
                continue
            else:
                flag = 1
                result = ' ' + result + '学号' + a[0]

        result = result + '的同学成绩录入失败，请检查！！'
        if flag == 0:
            return redirect(url_for('excel', bianhao=bianhao, result='成绩单导入成功，请点击成绩中心进行查看！'))
        else:
            return redirect(url_for('excel', bianhao=bianhao, result=result))
    else:
        bianhao = request.args.get('bianhao')
        return redirect(url_for('excel', bianhao=bianhao))

#将所有的教师授课信息显示出来
@app.route('/course', methods=['POST', 'GET'])
def course():
    r = request.args.get('result', '')#？？？
    #查询教师授课表
    result,_ = GetSql2("select * from tea_cou")
    #查询开课班级表
    for i in range(len(result)):
        result1, _ = GetSql2("select 名称 from open_cou, class where open_cou.班级号 = class.班级号 and 课程编号 = '"+str(result[i][0])+"' and 课序号 = '"+str(result[i][1])+"'")
        result[i] = (result[i], result1)#？？？？？
    return render_template("alreadyclass.html", results=result, result=r)
    # return render_template("man_cou.html", results=result, result=r)



#添加开设课程
@app.route('/add_open_cou', methods=['POST', 'GET'])
def add_open_cou():
    if request.method == 'POST':
        #获取信息
        kehao = request.form.get('kehao')
        kexuhao = request.form.get('kexuhao')
        tea = request.form.get('tea')
        num = request.form.get('num')
        kaike = request.form.get('kaike')
        didian = request.form.get('didian')
        zhou = request.form.get('zhou')
        xing = request.form.get('xing')
        jie = request.form.get('jie')
        opens = request.form.getlist('open')
        #将开课信息存储到数据库
        data = dict(
            课程编号 = kehao,
            课序号 = kexuhao,
            任课教师 = tea,
            选课人数上限 = num,
            开课学期 = kaike,
            上课地点 = didian,
            周数 =zhou,
            星期 = xing,
            节数 = jie
        )
        result = InsertData1(data, "tea_cou")
        for o in opens:
            data1 = dict(课程编号=kehao, 课序号=kexuhao, 班级号=o)
            InsertData1(data1, "open_cou")

        return redirect(url_for('course', result=result))
    else:
        return redirect(url_for('add_open'))







#查询开设课程
@app.route('/cha_kai', methods=['POST'])
def cha_kai():
    r = request.args.get('result', '')
    kehao = request.form.get('kehao')
    kexuhao = request.form.get('kexuhao')
    #查询该课程的开课信息
    # 查询教师授课表
    result, _ = GetSql2("select * from tea_cou where 课程编号 = '"+str(kehao)+"' and 课序号 = '"+str(kexuhao)+"'")
    # 查询开课班级表
    for i in range(len(result)):
        result1, _ = GetSql2("select 名称 from open_cou, class where open_cou.班级号 = class.班级号 and 课程编号 = '" + str(
            result[i][0]) + "' and 课序号 = '" + str(result[i][1]) + "'")
        result[i] = (result[i], result1)
    #[(('12301', 1, '45601', 50, '1', '商学院101', '1-18', 1, 2), [('计算机科学与技术',), ('数字媒体技术',)])]
    return render_template("man_cou.html", results=result, result=r)

#批量输入成绩
@app.route('/piliang', methods=['GET'])
def piliang():
    kehao = request.args.get('kehao')
    kexuhao = request.args.get('kexuhao')
    bianhao = request.args.get('bianhao')
    r = request.args.get('result', '')  # 默认值设为空
    #查询这门课的所有学生
    result, _ = GetSql2("select 学号, 平时成绩, 考试成绩 from stu_cou where 课程编号 = '"+str(kehao)+"' and 课序号 = '"+str(kexuhao)+"'")
    return render_template("piliang.html", results=result, result=r, kehao=kehao, kexuhao=kexuhao, bianhao=bianhao)

#修改开设课程
@app.route('/xiu_open_cou', methods=['POST'])
def xiu_open_cou():
    kehao = request.form.get('kehao')
    kexuhao = request.form.get('kexuhao')
    tea = request.form.get('tea')
    num = request.form.get('num')
    kaike = request.form.get('kaike')
    didian = request.form.get('didian')
    zhou = request.form.get('zhou')
    xing = request.form.get('xing')
    jie = request.form.get('jie')
    opens = request.form.getlist('open')
    #将数据存储到数据库中
    data = dict(
        课程编号=kehao,
        课序号=kexuhao,
        任课教师=tea,
        选课人数上限=num,
        开课学期=kaike,
        上课地点=didian,
        周数=zhou,
        星期=xing,
        节数=jie
    )
    result1 = UpdateData2("update tea_cou set 任课教师 = '"+str(tea)+"', 选课人数上限 = "+str(num)+", 开课学期 = '"+str(kaike)+"', 上课地点 = '"+str(didian)+"', 周数='"+str(zhou)+"', 星期="+str(xing)+", 节数="+str(jie)+" where 课程编号 = '"+str(kehao)+"' and 课序号 = '"+str(kexuhao)+"'")
    for o in opens:
        data1 = dict(课程编号=kehao, 课序号=kexuhao, 班级号=o)
        UpdateData2("update open_cou set 班级号 = '"+str(o)+"' where 课程编号 = '"+str(kehao)+"' and 课序号 = '"+str(kexuhao)+"'")

    return redirect(url_for('course', result=result1))

#批量输入成绩，进行录入
@app.route('/piliang_luru', methods=['POST'])
def piliang_luru():
    xuehao = request.form.get('xuehao')
    kehao = request.form.get('kehao')
    kexuhao = request.form.get('kexuhao')
    ping = request.form.get('pingshi')
    kao = request.form.get('kaoshi')
    #将数据存储到数据库中
    result = UpdateData1("update stu_cou set 平时成绩 = "+str(ping)+", 考试成绩 = "+str(kao)+" where 学号 = '"+str(xuehao)+"' and 课程编号 = '"+str(kehao)+"' and 课序号 = '"+str(kexuhao)+"'")

    return redirect(url_for('piliang', result=result, kehao=kehao, kexuhao=kexuhao))


#个人中心
@app.route('/sysinfo', methods=['POST', 'GET'])
def sysinfo():
    #查询个人账号
    result,_= GetSql2("select * from sys_user")
    if result:
        return render_template("sysinfo.html", username= result[0][0])

#个人中心修改密码
@app.route('/update_syspwd', methods=['POST', 'GET'])
def update_syspwd():
    username = request.form.get('username')
    password = request.form.get('pwd')
    # 创建md5对象
    m = hashlib.md5()
    b = password.encode(encoding='utf-8')
    m.update(b)
    password_md5 = m.hexdigest()
    #查询教师授课表
    result= UpdateData1("update sys_user set userpwd ='"+password_md5+"' where username='"+username+"'")
    
    if  result:
        flash("修改成功！")
        return render_template("sysinfo.html", username= username)
        # return redirect(url_for('index'))  # 密码错误重定向到登录页面

#学生信息管理
@app.route('/student_info',methods=['POST','GET'])
def student_info():
    #查询全部学生信息
    result,_= GetSql2("select * from student")
    if result:
        # print(result)
        return render_template("studentinfo.html",info = result)

#教师信息管理
@app.route('/teacher_info',methods=['POST','GET'])
def teacher_info():
    #查询全部学生信息
    result,_= GetSql2("select * from teacher")
    if result:
        # print(result)
        return render_template("teacherinfo.html",info = result)


#课程信息管理
@app.route('/class_info',methods=['POST','GET'])
def class_info():
    #查询全部学生信息
    result,_= GetSql2("select * from course")
    if result:
        print(result)
        return render_template("classinfo.html",info = result)


#学生信息管理新增
@app.route('/student_add',methods=['POST','GET'])
def student_add():
    #查询全部学生信息
    result,_= GetSql2("select * from student")
    if result:
        # print(result)
        return render_template("studentinfo.html",info = result)


#教师信息管理新增
@app.route('/teacher_add',methods=['POST','GET'])
def teacher_add():
    #查询全部学生信息
    result,_= GetSql2("select * from teacher")
    if result:
        # print(result)
        return render_template("teacherinfo.html",info = result)


#课程信息管理新增
@app.route('/class_add',methods=['POST','GET'])
def class_add():
    #查询全部学生信息
    result,_= GetSql2("select * from course")
    if result:
        # print(result)
        return render_template("classinfo.html",info = result)


#学生信息管理新增
@app.route('/student_query',methods=['POST','GET'])
def student_query():
    #查询全部学生信息
    result,_= GetSql2("select * from student")
    if result:
        # print(result)
        return render_template("studentinfo.html",info = result)

#教师信息管理新增
@app.route('/teacher_query',methods=['POST','GET'])
def teacher_query():
    #查询全部学生信息
    result,_= GetSql2("select * from teacher")
    if result:
        # print(result)
        return render_template("teacherinfo.html",info = result)

#教师信息管理新增
@app.route('/class_query',methods=['POST','GET'])
def class_query():
    #查询全部学生信息
    result,_= GetSql2("select * from course")
    if result:
        # print(result)
        return render_template("classinfo.html",info = result)


#添加开设课程页面
@app.route('/add_open', methods=['POST', 'GET'])
def add_open():
    #把没有开课的课程编号传过去
    kehao, _ = GetSql2("select 课程编号 from course where 课程编号 not in (select 课程编号 from tea_cou)")
    #查询所有的教师编号传过去
    bianhao, _ = GetSql2("select 编号 from teacher")
    banhao, _ = GetSql2("select 班级号 from class")
    return render_template("addalreadyclass.html", kehao=kehao, tea=bianhao, ban= banhao)




#修改开设课程页面
@app.route('/xiu_open', methods=['GET'])
def xiu_open():
    #将数据查询出来，传递给修改界面
    # kehao = request.args.get('kehao')
    # kexuhao = request.args.get('kexuhao')
    # tea = request.args.get('tea')
    # # 查询教师授课表
    # result, _ = GetSql2("select * from tea_cou where 课程编号 = '"+str(kehao)+"' and 课序号 = '"+str(kexuhao)+"' and 任课教师 = '"+str(tea)+"'")
    # # 查询开课班级表
    # for i in range(len(result)):
    #     op = []
    #     result1, _ = GetSql2("select class.班级号 from open_cou, class where open_cou.班级号 = class.班级号 and 课程编号 = '" + str(
    #         result[i][0]) + "' and 课序号 = '" + str(result[i][1]) + "'")
    #     for r in result1:
    #         op.append(r[0])
    #     result[i] = (result[i], op)
    # #将所有任课教师查询出来
    # teachers, _ = GetSql2("select 编号 from teacher")
    # #将所有的班级查询出来
    # bans,_ = GetSql2("select 班级号 from class")
    return render_template("xiualreadyclass.html")
# results=result[0], teachers=teachers, ban=bansv




#删除开设课程
@app.route('/del_open', methods=['GET', 'POST'])
def del_open():
    if request.method == 'GET':#是单独删除tea_cou:课；     open_cou：开起来的课
        kexuhao = request.args.get('kexuhao')
        sql1 = "delete from tea_cou where  课序号 = '"+str(kexuhao)+"'"
        result1 = DelDataById1(sql1)
        sql2 = "delete from open_cou where  课序号 = '"+str(kexuhao)+"'"
        result2 = DelDataById1(sql2)
        if result1 == '删除成功' and result2 == '删除成功':
            result = '删除成功'
        else:
            result = '删除失败'
        return redirect(url_for('course', result=result))
    else:
        #是批量删除
        couids = request.form.getlist('couid')
        # couid是列表的形式，['12301+1+45601', '12302+1+45602']，用字典的方式获取数据
        ke = []
        flag = 0
        for couid in couids:
            #第一个加号的位置
            index = couid.find('+')
            #第二个加号的位置
            index2 = couid.find('+', index+1)
            dic = {}
            dic['kehao'] = couid[:index]
            dic['kexuhao'] = couid[index + 1:index2]
            dic['tea'] = couid[index2+1:]
            #将数据库中的信息删除
            result1 = DelDataById1("delete from tea_cou where 课程编号 = '"+str(dic['kehao'])+"' and 课序号 = '"+str(dic['kexuhao'])+"' and 任课教师 = '"+str(dic['tea'])+"'")
            result2 = DelDataById1("delete from open_cou where 课程编号 = '"+str(dic['kehao'])+"' and 课序号 = '"+str(dic['kexuhao'])+"'")
            if result1 == '删除成功' and result2 == '删除成功':
                continue
            else:
                flag = 1
        if flag == 1:
            result = '删除失败'
        else:
            result = '删除成功'
        return redirect(url_for('course', result=result))
if __name__ == '__main__':
   app.run(debug = True,port=5000)