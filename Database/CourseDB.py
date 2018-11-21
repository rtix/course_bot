import sqlite3 as sql

def create_course(owner_id,course_name):
    con = sql.connect('./Database/DB_FOR_TBOT.db')
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("Insert into Course(name,owner) values(?,?)",[course_name,owner_id])
    con.commit()
    cur.execute("""Select id from Course
                    where owner=? and name = ?""",[owner_id,course_name])
    c=cur.fetchall()
    con.close()
    return c
def create_user_course(id_user,id_course):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("Insert into User_course(id_user,id_course) values(?,?)",[id_user,id_course])
    con.commit()
    con.close()
def get_course(course_id):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("""Select * from Course
                where id=?""",[course_id])
    res = cur.fetchall()[0]
    d = {'name': res[0], 'owner': res[1], 'description': res[2], 'id': res[3]}
    con.close()
    return d
def get_course_participants(course_id):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("""Select id_user from User_course
                where id_course=?""",[course_id])
    res=cur.fetchall()
    c=[]
    for i in res:
        c.append(i[0])
    con.close()
    return c
def create_task(course_id,task_name,task_descr,task_highest_mark):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Insert into Tasks(course_id,description,max_ball,name) values(?,?,?,?)"""
                ,[course_id,task_descr,task_highest_mark,task_name])
    con.commit()
    cur.execute("""Select number from Tasks
                where course_id=? and name=?""",[course_id,task_name])
    c=cur.fetchall()[0][0]
    con.close()
    return c
def get_task(course_id,task_id):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("""Select* from Tasks
                where course_id=? and task_id =?""",[course_id,task_id])
    res=cur.fetchall()[0]
    d={'course_id':res[0],'description':res[1],'max_ball':res[2],'name':res[3],'task_id':res[4],'deadline':res[5]}
    con.close()
    return d
def set_course(course_id,field, value):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Update Course
                Set {}=?
                where id=?""".format(field),[value,course_id])
    con.commit()
    con.close()
    return course_id
def set_task(course_id,task_id,field,value):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Update Tasks
                Set {}=?
                where course_id=? and task_id=?""".format(field),[value,course_id,task_id])
    con.commit()
    con.close()
    return course_id
def delete_course(course_id):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Delete from Course
                where id=?""",[course_id])
    con.commit()
    con.close()
    return course_id
def create_mark(course_id,task_id,user_id,mark,date):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Insert into Marks values(?,?,?,?,?)""",[mark,task_id,user_id,course_id,date])
    con.commit()
    con.close()
    return task_id
def get_mark(course_id,task_id,user_id):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Select * from Marks
                where course_id=? and task_id=? and user_id=?""",[course_id,task_id,user_id])
    c=cur.fetchall()[0]
    con.close()
    d={'mark':c[0],'task_id':c[1],'user_id':c[2],'course_id':c[3],'date':c[4]}
    return d
def set_mark(course_id,task_id,user_id,field,value):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Update Marks
                Set {}=?
                where course_id=? and task_id=? and user_id=?""".format(field),[value,course_id,task_id,user_id])
    con.commit()
    con.close()
    return task_id
def delete_mark(course_id,task_id,user_id):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Delete from Marks
                where course_id=? and task_id=? and user_id=?""",[course_id,task_id,user_id])
    con.commit()
    con.close()
    return task_id
def delete_task(course_id,task_id):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Delete from Tasks
                where course_id=? and task_id=?""",[course_id,task_id])
    con.commit()
    con.close()
    return task_id
def create_classwork(course_id,cw_name,cw_date):
    con=sql.connect("./Database/DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Insert into Classworks(course_id,name,date) values(?,?,?)""",[course_id,cw_name,cw_date])
    con.commit()
    cur.execute("""Select classwork_id from Classworks
                where course_id= ? and name= ? and date =?""",[course_id,cw_name,cw_date])
    c=cur.fetchall()
    con.close()
    return c[0][0]
def set_classwork(course_id,cw_id,field,value):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Update Classworks
                Set {} = ?
                where course_id = ? and classwork_id=?""".format(field),[value,course_id,cw_id])
    con.commit()
    con.close()
    return 1
def delete_classwork(course_id,cw_id):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Delete from Classworks
                where course_id=? and classwork_id=?""",[course_id,cw_id])
    con.commit()
    con.close()
    return cw_number
def get_classwork(course_id,cw_id):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Select * from Classworks
                where course_id=? and classwork_id=?""",[course_id,cw_id])
    con.commit()
    c=cur.fetchall()[0]
    con.close()
    if c:
        d={'course_id':c[0],'classwork_id':c[1],'name':c[2],'date':c[3]}
        return d
    else:
        return None
def create_attendance(course_id,cw_id,user_id,value):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Insert into Attendance values(?,?,?,?)""",[course_id,cw_id,user_id,value])
    con.commit()
    con.close()
    return 1
def get_attendance(course_id,cw_id,user_id):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Select * from Attendance
                where course_id=? and cw_number=? and user_id=?""",[course_id,cw_id,user_id])
    c=cur.fetchall()
    con.close()
    if c:
        c=c[0]
        d={'course_id':c[0],'cw_id':c[1],'user_id':c[2],'value':c[3]}
        return d
    else:
        return None
def set_attendance(course_id,cw_id,user_id,field,value):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Update Attendance
                Set {}=?
                where course_id=? and cw_number=? and user_id=?""".format(field),[value,course_id,cw_id,user_id])
    con.commit()
    con.close()
    return 1
def delete_attendance(course_id,cw_id,user_id):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Delete from Attendance
                where course_id=? and user_id=? and cw_number=?""",[course_id,user_id,cw_id])
    con.commit()
    con.close()
    return 1
