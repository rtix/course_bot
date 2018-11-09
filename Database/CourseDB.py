import sqlite3 as sql
con = sql.connect("CourseDB.db")

def create_course(owner_id,course_name):
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("Insert into course(name,owner) values(?,?)",[course_name,owner_id])
    con.commit()
    cur.execute("""Select id from Course
                    where owner=? and name = ?""",[owner_id,course_name])
    c=cur.fetchall()
    return c
def create_user(username):
    cur = con.cursor()
    cur.execute("Insert into User(username) values(?)",[username])
    con.commit()
def create_user_course(id1,id2):
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("Insert into User_course(id_user,id_course) values(?,?)",[id1,id2])
    con.commit()

def get_course(course_id):#это тоже
    cur = con.cursor()
    cur.execute("""Select * from Course
                where id=?""",[course_id])
    res = cur.fetchall()[0]
    d = {'name': res[0], 'owner': res[1], 'description': res[2], 'id': res[3]}
    return d
def get_course_participants(course_id):
    cur=con.cursor()
    cur.execute("""Select* from User_course
                where id_course=?""",[course_id])
    res=cur.fetchall()
    c=[]
    for i in res:
        c.append(i[1])
    return c
def create_task(course_id,task_numb,task_descr,task_highest_mark):
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("Insert into Tasks values(?,?,?,?)",[course_id,task_descr,task_highest_mark,
                                                    task_numb])
    con.commit()
    return course_id
def get_task(course_id,task_number):
    cur=con.cursor()
    cur.execute("""Select* from Tasks
                where course_id=? and number =?""",[course_id,task_number])
    res=cur.fetchall()[0]
    d={'course_id':res[0],'description':res[1],'max_ball':res[2],'number':res[3]}
    return d
def set_course(course_id,field, value):
    cur=con.cursor()
    cur.execute("Pragma foreign keys = ON")
    con.commit()
    cur.execute("""Update Course 
                Set {}=?
                where id=?""".format(field),[value,course_id])
    con.commit()
    return course_id
def set_task(course_id,task_number,field,value):
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Update Tasks
                Set {}=?
                where course_id=? and number=?""".format(field),[value,course_id,task_number])
    con.commit()
    return course_id
con.close()
