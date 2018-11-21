import sqlite3 as sql

def get_user_by_id(user_id):
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
        return None
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
    return 1
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
def add_course_stud(stud_id,course_id):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Insert into User_Course(id_user,id_course) values (?,?)""",[stud_id,course_id])
    con.commit()
    con.close()
    return stud_id
def del_course_stud(stud_id,course_id):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Delete from User_course
                where id_user=? and id_course=?""",[stud_id,course_id])
    con.commit()
    con.close()
    return stud_id
def write_teacher_username(username,name):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("""Insert into Teacher_username values(?,?)""",[username,name])
    con.commit()
def is_teacher_username(username):
    con = sql.connect("./Database/DB_FOR_TBOT.db")
    cur = con.cursor()
    cur.execute("""Select name from Teacher_username
                where username=?""",[username])
    c = cur.fetchall()
    if(c):
        cur.execute("""Delete from Teacher_username
                    where username=?""",[username])
        con.commit()
        return [1,c[0][0]]
    else:
        return [0,'']
