import sqlite3 as sql

def get_user(user_id):
    '''
    Возвращает словарь полей по id
    :param id: id- идентификатор юзера
    :return: словарь всех данных
    '''
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("""Select* from User
                    where u_id=?""", [user_id])
    c=cur.fetchall()
    con.close()
    if c:
        res = c[0]
        d = {'name': res[0], 'group_n': res[1], 'email': res[2], 'type_u': res[3], 'u_id': res[4]}
        return d
    else:
        return None

def get_user_courses(user_id):
    '''
    Возвращает list курсов, на которые записан user c id_user = user_id
    :param user_id: user_id - номер(идентификатор) user`а
    :return: list номеров(идентификаторов) курсов, на которые записан данный user
    '''
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("""Select id_course from User_course
                where id_user=?""",[user_id])
    c=cur.fetchall()
    res=c
    if c:
        if len(c)>1:
            a=[]
            for i in res:
                a.append(i[0])
            con.close()
            return a
        else:
            res=c[0]
            con.close()
            return list(res)
    else:
        return []

def set_user(user_id,field,value):
    '''
    В поле field таблицы User записывает значение value
    :param user_id: номер(идентификатор) user`a
    :param field: поле таблицы User. Например, 'group_n' или 'name'
    :param value: значение, которое записывается в field
    :return: здесь это не важно, поэтому я просто возвращаю user_id
    '''
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Update User
                Set {} = ?
                where u_id=?""".format(field),[value,user_id])
    con.commit()
    con.close()
    return user_id

def create_user(id,name,group,email,type_u):
    """
    Паша, ну тут понятно, что делает функция.
    Единственное, я не знаю, что возвращать, поэтому верну единичку
    :param username:
    :param name:
    :param group:
    :param email:
    :param type_u:
    :return:
    """
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Insert into User values(?,?,?,?,?)""",[name,group,email,type_u,id])
    con.commit()
    con.close()
    
def get_teacher_courses(id_teacher):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("""Select id from Course
                where owner =?""",[id_teacher])
    res=cur.fetchall()
    con.close()
    a=[]
    for i in res:
        a.append(i[0])
    return a

def create_teacher_invitation(username):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("""Select username from Teacher_invitation
                where username=?""",[username])
    c=cur.fetchone()
    if not c:
        cur.execute("""Insert into Teacher_invitation values(?)""",[username])
        con.commit()
        con.close()
    else:
        con.close()

def delete_teacher_invitation(username):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("""Delete from Teacher_invitation
                where username = ?""",[username])
    con.commit()
    con.close()

def check_teacher_invitation(username):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("""Select username from Teacher_invitation
                where username = ?""",[username])
    c=cur.fetchone()
    if not c:
        return False
    else:
        return True
        
def fetch_all_users():
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("""Select u_id from User""")
    c=cur.fetchall()
    if c:
        a = []
        for i in c:
            a.append(i[0])
        return a
    else:
        return []

def fetch_all_teachers():
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    type='teacher'
    cur.execute("""Select u_id from User
                where type_u=?""",[type])
    c = cur.fetchall()
    if c:
        a = []
        for i in c:
            a.append(i[0])
        return a
    else:
        return []
