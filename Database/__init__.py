from Database.CourseDB import *
from Database.UserDB import *
import sqlite3
# Create users database, if it's not exists yet
con = sqlite3.connect("DB_FRO_TBOT.db")
con.cursor().execute("""Create table if not exists User(
                username text,
                name text,
                group_n text,
                email text,
                type_u text,
                u_id integer not null primary key AUTOINCREMENT)""")
con.commit()
con.cursor().execute("""Create table if not exists Course(
                name text not null,
                owner integer not null,
                description text,
                id integer not null primary key AUTOINCREMENT,
                foreign key(owner) references User(u_id))""")
con.commit()
con.cursor().execute("""Create table if not exists User_course(
                id_user integer not null,
                id_course integer not null,
                primary key(id_user,id_course),
                foreign key(id_user) references User(u_id),
                foreign key(id_course) references Course(id))""")
con.commit()
con.cursor().execute("""Create table if not exists Tasks(
                course_id integer not null,
                description text,
                max_ball float,
                number integer not null,
                primary key(course_id,number),
                foreign key(course_id) references Course(id))""")
con.commit()
con.cursor().execute("""Create table if not exists Marks(
                mark integer,
                task_num integer not null,
                user_id integer not null,
                course_id integer not null,
                foreign key(course_id,task_num) references Tasks(course_id,number),
                foreign key(user_id) references User(u_id))""")
con.commit()
con.close()
