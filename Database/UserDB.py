import sqlite3 as sql

def get_user(id,username):
    '''
    Возвращает словарь полей по id и username
    :param id: id- идентификатор юзера, username - имя пользователя из table user
    :return: словарь всех данных
    '''
    con = sql.connect("DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("""Select* from User
                where u_id=? and username=?""",[id,username])
    res=cur.fetchall()[0]
    d={'username': res[0],'name':res[1],'group_n':res[2],'email':res[3],'type_u':
    res[4],'u_id':res[5]}
    con.close()
    return d
def get_user_courses(user_id):
    '''
    Возвращает list курсов, на которые записан user c id_user = user_id
    :param user_id: user_id - номер(идентификатор) user`а
    :return: list номеров(идентификаторов) курсов, на которые записан данный user
    '''
    con = sql.connect("DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("""Select* from User_course
                where id_user=?""",[user_id])
    res=cur.fetchall()[1]
    con.close()
    return res
def set_user(user_id,field,value):
    '''
    В поле field таблицы User записывает значение value
    :param user_id: номер(идентификатор) user`a
    :param field: поле таблицы User. Например, 'group_n' или 'name'
    :param value: значение, которое записывается в field
    :return: здесь это не важно, поэтому я просто возвращаю user_id
    '''
    con = sql.connect("DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Update User
                Set {} = ?
                where u_id=?""".format(field),[value,user_id])
    con.commit()
    con.close()
    return user_id
def create_user(username,name,group,email,type_u):
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
    con = sql.connect("DB_FOR_TBOT.db")
    cur=con.cursor()
    cur.execute("Pragma foreign_keys = ON")
    con.commit()
    cur.execute("""Insert into User(username,name,group_n,email,type_u) values(?,?,?,?,?)""",[username,name,group,email,type_u])
    con.commit()
    con.close()
    return 1
