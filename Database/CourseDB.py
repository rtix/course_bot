from Bot.config import DATABASE_PATH
import sqlite3 as sql

def create_course(owner_id,course_name):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Select Max(id)
                    from Course""")
    c = cur.fetchone()[0]
    if c is None:
        c = 1
    else:
        c = c + 1
    cur.execute("Insert into Course(name,owner,id) values(?,?,?)",[course_name,owner_id,c])
    con.commit()
    return c

def create_user_course(id_user,id_course):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("Insert into User_course(id_user,id_course) values(?,?)",[id_user,id_course])
    con.commit()
    con.close()

def get_course(course_id):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("""Select * from Course
                where id=?""",[course_id])
    res = cur.fetchall()[0]
    cur.execute("""Select id_user from User_course
                where id_course=?""",[course_id])
    res1=cur.fetchall()
    if res1:
        a = []
        for i in res1:
            a.append(i[0])
    else:
        a=[]
    cur.execute("""Select user_id from Blacklist 
                where course_id=?""",[course_id])
    res2=cur.fetchall()
    if res2:
        b = []
        for i in res2:
            b.append(i[0])
    else:
        b=[]
    cur.execute("""Select task_id from Tasks
                where course_id=?""",[course_id])
    res3=cur.fetchall()
    if res3:
        c = []
        for i in res3:
            c.append(i[0])
    else:
        c=[]
    cur.execute("""Select classwork_id from Classworks
                where course_id=?""",[course_id])
    res4=cur.fetchall()
    if res4:
        e = []
        for i in res4:
            e.append(i[0])
    else:
        e=[]
    cur.execute("""Select lit_id from Literature 
                where course_id=?""",[course_id])
    res5=cur.fetchall()
    if res5:
        f = []
        for i in res5:
            f.append(i[0])
    else:
        f=[]
    con.close()
    d = {'name': res[0], 'owner': res[1], 'description': res[2], 'id': res[3],
         'entry_restriction':res[4], 'participants': a, 'blacklist': b,
         'task_numbers': c, 'cw_numbers': e, 'lit_numbers': f}
    con.close()
    return d

def get_course_participants(course_id):
    con = sql.connect(DATABASE_PATH)
    cur=con.cursor()
    cur.execute("""Select id_user from User_course
                where id_course=?""",[course_id])
    res=cur.fetchall()
    c=[]
    for i in res:
        c.append(i[0])
    con.close()
    return c

def create_task(course_id,task_name,task_descr,task_highest_mark,deadline):
    con = sql.connect(DATABASE_PATH)
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Select Max(task_id)
                    from Tasks""")
    c = cur.fetchone()[0]
    if c is None:
        c = 1
    else:
        c = c + 1
    cur.execute("""Insert into Tasks(course_id,description,highest_mark,name,deadline)
                values(?,?,?,?,?)"""
                ,[course_id,task_descr,task_highest_mark,task_name,deadline])
    con.commit()
    return c

def get_task(course_id,task_id):
    con = sql.connect(DATABASE_PATH)
    cur=con.cursor()
    cur.execute("""Select* from Tasks
                where course_id=? and task_id =?""",[course_id,task_id])
    res=cur.fetchall()[0]
    d={'course_id':res[0],'description':res[1],'highest_mark':res[2],'name':res[3],'task_id':res[4],'deadline':res[5]}
    con.close()
    return d

def set_course(course_id,field,value):
    con = sql.connect(DATABASE_PATH)
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
    con = sql.connect(DATABASE_PATH)
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
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Delete from Course
                where id=?""",[course_id])
    con.commit()
    con.close()
    return course_id

def create_mark(course_id,task_id,user_id,mark,date):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Insert into Marks values(?,?,?,?,?)""",[mark,task_id,user_id,course_id,date])
    con.commit()
    con.close()
    return task_id

def get_mark(course_id,task_id,user_id):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Select * from Marks
                where course_id=? and task_id=? and user_id=?""",[course_id,task_id,user_id])
    try:
        c=cur.fetchall()[0]
    except IndexError:
        return {}
    con.close()
    d={'mark':c[0],'task_id':c[1],'user_id':c[2],'course_id':c[3],'date':c[4]}
    return d

def set_mark(course_id,task_id,user_id,field,value):
    con = sql.connect(DATABASE_PATH)
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
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Delete from Marks
                where course_id=? and task_id=? and user_id=?""",[course_id,task_id,user_id])
    con.commit()
    con.close()
    return task_id

def delete_task(course_id,task_id):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Delete from Tasks
                where course_id=? and task_id=?""",[course_id,task_id])
    con.commit()
    con.close()
    return task_id

def create_classwork(course_id,cw_name,cw_date):
    con=sql.connect(DATABASE_PATH)
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Select Max(classwork_id)
                from Classworks""")
    c=cur.fetchone()[0]
    if c is None:
        c=1
    else:
        c=c+1
    cur.execute("""Insert into Classworks(course_id,name,date) values(?,?,?)""",
                [course_id,cw_name,cw_date])
    con.commit()
    con.close()
    return c

def set_classwork(course_id,cw_id,field,value):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Update Classworks
                Set {} = ?
                where course_id = ? and classwork_id=?""".format(field),[value,course_id,cw_id])
    con.commit()
    con.close()
    
def delete_classwork(course_id,cw_id):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Delete from Classworks
                where course_id=? and classwork_id=?""",[course_id,cw_id])
    con.commit()
    con.close()
    return cw_id

def get_classwork(course_id,cw_id):
    con = sql.connect(DATABASE_PATH)
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
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Insert into Attendance values(?,?,?,?)""",[course_id,cw_id,user_id,value])
    con.commit()
    con.close()
    
def get_attendance(course_id,cw_id,user_id):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Select * from Attendance
                where course_id=? and cw_id=? and user_id=?""",[course_id,cw_id,user_id])
    c=cur.fetchall()
    con.close()
    if c:
        c=c[0]
        d={'course_id':c[0],'cw_id':c[1],'user_id':c[2],'value':c[3]}
        return d
    else:
        return {}

def set_attendance(course_id,cw_id,user_id,field,value):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Update Attendance
                Set {}=?
                where course_id=? and cw_id=? and user_id=?""".format(field),[value,course_id,cw_id,user_id])
    con.commit()
    con.close()
    
def delete_attendance(course_id,cw_id,user_id):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Delete from Attendance
                where course_id=? and user_id=? and cw_id=?""",[course_id,user_id,cw_id])
    con.commit()
    con.close()
    
def append_to_blacklist(course_id,user_id):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Insert into Blacklist values (?,?)""",[course_id,user_id])
    con.commit()
    con.close()
    
def remove_from_blacklist(course_id,user_id):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Delete from Blacklist
                where course_id=? and user_id=?""",[course_id,user_id])
    con.commit()
    con.close()
    
def append_user_course(stud_id,course_id):
    con = sql.connect(DATABASE_PATH)
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Insert into User_Course(id_user,id_course) values (?,?)""",[stud_id,course_id])
    con.commit()
    con.close()
    return stud_id

def remove_user_course(stud_id,course_id):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Delete from User_course
                where id_user=? and id_course=?""",[stud_id,course_id])
    con.commit()
    con.close()
    return stud_id

def create_literature(course_id,name, description, file_id, url):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("""Insert into Literature(course_id,name,description,file_id,url)
                values(?,?,?,?,?)""",[course_id,name,description,file_id,url])
    con.commit()
    cur.execute("""Select Max(lit_id) from Literature
                where course_id = ? and name= ?""",[course_id,name])
    d=cur.fetchone()[0]
    con.close()
    return d

def get_literature(course_id,lit_id):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Select file_id from Literature
                where course_id=? and lit_id=?""",[course_id,lit_id])
    d=cur.fetchone()
    if d:
        con.close()
        d=d[0]
        return d
    else:
        con.close()
        
def set_literature(course_id, lit_id,field,value):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Update Literature
                Set {}=?
                where course_id=? and lit_id=?""".format(field),[value,course_id,lit_id])
    con.commit()
    con.close()
    
def delete_literature(course_id, lit_id):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("""Delete from Literature
                where course_id=? and lit_id=?""",[course_id,lit_id])
    con.commit()
    con.close()
    return lit_id

def fetch_all_courses():
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("""Select id from Course""")
    c=cur.fetchall()
    if c is None:
        con.close()
        return None
    else:
        a = []
        for i in c:
            a.append(i[0])
        return a
