import sqlite3

# sqlite 帮助
def OpenDb():
    # 数据库地址
    database = "./database/data/data.db"
    conn = sqlite3.connect(database)
    return conn

def GetSql(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    fields = []
    for field in cur.description:
        fields.append(field[0])
    result = cur.fetchall()
    # for item in result:
    #     print(item)
    cur.close()
    return result, fields

def CloseDb(conn):
    conn.close()

def GetSql2(sql):
    conn = OpenDb()
    result, fields = GetSql(conn, sql)
    CloseDb(conn)
    return result, fields

def UpdateData(data, tablename):
    result = ""
    conn = OpenDb()
    values = []
    cusor = conn.cursor()
    idName = list(data)[0]
    for v in list(data)[1:]:
        values.append("%s='%s'" % (v, data[v]))
    sql = "update %s set %s where %s='%s'" % (tablename, ",".join(values), idName, data[idName])
    # print(sql)
    try:
        cusor.execute(sql)
        conn.commit()
        result = "修改成功"
    except Exception as e:
        conn.rollback()
        result = "修改失败"
    cusor.close()
    CloseDb(conn)
    return result

def InsertData(data, tablename):
    conn = OpenDb()
    values = []
    cusor = conn.cursor()
    fieldNames = list(data)
    for v in fieldNames:
        values.append(data[v])
    sql = "insert into  %s (%s) values( %s) " % (tablename, ",".join(fieldNames), ",".join(["?"] * len(fieldNames)))
    # print(sql)
    try:
        cusor.execute(sql, values)
        conn.commit()
        result = "选课成功"
    except Exception as e:
        conn.rollback()
        result = "选课失败"
    cusor.close()
    CloseDb(conn)
    return result

def DelDataById(sql):
    conn = OpenDb()
    cusor = conn.cursor()
    # print (sql)
    try:
        cusor.execute(sql)
        conn.commit()
        result = "退课成功"
    except Exception as e:
        conn.rollback()
        result = "退课失败"
    cusor.close()
    CloseDb(conn)
    return result

def UpdateData1(sql):
    result = ""
    conn = OpenDb()
    values = []
    cusor = conn.cursor()
    try:
        cusor.execute(sql)
        conn.commit()
        result = "成绩录入成功"
    except Exception as e:
        conn.rollback()
        result = "成绩录入失败"
    cusor.close()
    CloseDb(conn)
    return result

def InsertData1(data, tablename):
    conn = OpenDb()
    values = []
    cusor = conn.cursor()
    fieldNames = list(data)
    for v in fieldNames:
        values.append(data[v])
    sql = "insert into  %s (%s) values( %s) " % (tablename, ",".join(fieldNames), ",".join(["?"] * len(fieldNames)))
    print(sql)
    try:
        cusor.execute(sql, values)
        conn.commit()
        result = "添加成功"
    except Exception as e:
        conn.rollback()
        result = "添加失败"
    cusor.close()
    CloseDb(conn)
    return result

def InsertDataV(sql):
    conn = OpenDb()
    cusor = conn.cursor()
    print(sql)
    try:
        cusor.execute(sql)
        conn.commit()
        result = "添加成功"
    except Exception as e:
        conn.rollback()
        result = "添加失败"
    cusor.close()
    CloseDb(conn)
    return result

def DelDataById1(sql):
    conn = OpenDb()
    cusor = conn.cursor()
    try:
        cusor.execute(sql)
        conn.commit()
        result = "删除成功"
    except Exception as e:
        conn.rollback()
        result = "删除失败"
    cusor.close()
    CloseDb(conn)
    return result

def UpdateData2(sql):
    result = ""
    conn = OpenDb()
    values = []
    cusor = conn.cursor()
    try:
        cusor.execute(sql)
        conn.commit()
        result = "修改成功"
    except Exception as e:
        conn.rollback()
        result = "修改失败"
    cusor.close()
    CloseDb(conn)
    return result