import sqlite3 as sql

def create_course(owner_id,course_name):
    con = sql.connect("DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("Insert into course(name,owner) values(?,?)",[course_name,owner_id])
    con.commit()
    cur.execute("""Select id from Course
                    where owner=? and name = ?""",[owner_id,course_name])
    c=cur.fetchall()
    con.close()
    return c
def create_user(username):
    con = sql.connect("DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Insert into User(username) values(?)",[username])
    con.commit()
    con.close()
def create_user_course(id1,id2):
    con = sql.connect("DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("Insert into User_course(id_user,id_course) values(?,?)",[id1,id2])
    con.commit()
    con.close()

def get_course(course_id):#это тоже
    con = sql.connect("DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("""Select * from Course
                where id=?""",[course_id])
    res = cur.fetchall()[0]
    d = {'name': res[0], 'owner': res[1], 'description': res[2], 'id': res[3]}
    con.close()
    return d
def get_course_participants(course_id):
    con = sql.connect("DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("""Select* from User_course
                where id_course=?""",[course_id])
    res=cur.fetchall()
    c=[]
    for i in res:
        c.append(i[1])
    con.close()
    return c
def create_task(course_id,task_numb,task_descr,task_highest_mark):
    con = sql.connect("DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("Insert into Tasks values(?,?,?,?)",[course_id,task_descr,task_highest_mark,
                                                    task_numb])
    con.commit()
    con.close()
    return course_id
def get_task(course_id,task_number):
    con = sql.connect("DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("""Select* from Tasks
                where course_id=? and number =?""",[course_id,task_number])
    res=cur.fetchall()[0]
    d={'course_id':res[0],'description':res[1],'max_ball':res[2],'number':res[3]}
    con.close()
    return d
def set_course(course_id,field, value):
    con = sql.connect("DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("Pragma foreign keys = ON")
    con.commit()
    cur.execute("""Update Course
                Set {}=?
                where id=?""".format(field),[value,course_id])
    con.commit()
    con.close()
    return course_id
def set_task(course_id,task_number,field,value):
    con = sql.connect("DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Update Tasks
                Set {}=?
                where course_id=? and number=?""".format(field),[value,course_id,task_number])
    con.commit()
    con.close()
    return course_id
