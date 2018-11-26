from Database.CourseDB import *
from Database.UserDB import *
from Database.RegistrationDB import*
import sqlite3
con = sqlite3.connect('./Database/DB_FOR_TBOT.db')
con.cursor().execute("""Create table if not exists User(
                name text,
                group_n text,
                email text,
                type_u text,
                u_id integer not null primary key)""")
con.commit()
con.cursor().execute("""Create table if not exists Teacher_username(
                    username text unique,
                    name text)""")
con.commit()
con.cursor().execute("""Create table if not exists Course(
                name text not null,
                owner integer not null,
                description text,
                id integer not null primary key AUTOINCREMENT,
                enry_restriction text,
                foreign key(owner) references User(u_id) on delete cascade)""")
con.commit()
con.cursor().execute("""Create table if not exists User_code(
                    user_id integer not null primary key,
                    long_code text,
                    email text)""")
con.commit()
con.cursor().execute("""Create table if not exists User_course(
                id_user integer not null,
                id_course integer not null,
                primary key(id_user,id_course),
                foreign key(id_user) references User(u_id) on delete cascade,
                foreign key(id_course) references Course(id) on delete cascade)""")
con.commit()
con.cursor().execute("""Create table if not exists Tasks(
                course_id integer not null,
                description text,
                max_ball float,
                name text,
                task_id integer not null primary key autoincrement,
                deadline text,
                foreign key(course_id) references Course(id) on delete cascade)""")
con.commit()
con.cursor().execute("""Create table if not exists Marks(
                mark integer,
                task_id integer not null,
                user_id integer not null,
                course_id integer not null,
                date text,
                primary key(task_id,user_id,course_id),
                foreign key(course_id) references Course(id) on delete cascade,
                foreign key(task_id) references Tasks(number) on delete cascade,
                foreign key(user_id) references User(u_id) on delete cascade)""")
con.commit()
con.cursor().execute("""Create table if not exists Classworks(
                     course_id integer not null,
                     classwork_id integer not NULL primary key autoincrement,
                     name text,
                     date text,
                     foreign key(course_id) references Course(id) on delete cascade)""")
con.commit()
con.cursor().execute("""Create table if not exists Attendance(
                    course_id integer not null,
                    cw_id integer not null,
                    user_id integer not null,
                    value integer,
                    primary key(course_id,cw_id,user_id),
                    foreign key(course_id) references Course(id) on delete cascade,
                    foreign key(cw_id) references Classworks(classwork_id) on delete cascade,
                    foreign key(user_id) references User(u_id) on delete cascade)""")
con.commit()
con.cursor().execute("""Create table if not exists Blacklist(
                    course_id integer not null,
                    user_id integer not null,
                    primary key(course_id,user_id),
                    foreign key(course_id) references Course(id) on delete cascade,
                    foreign key(user_id) references User(u_id) on delete cascade)""")
con.commit()
con.cursor().execute("""Create table if not exists Literature(
                    course_id integer not null,
                    lit_id integer not null primary key autoincrement,
                    name text unique,
                    description text,
                    file_id integer,
                    url text,
                    foreign key(course_id) references Course(id) on delete cascade)
                    """)
con.commit()
con.close()