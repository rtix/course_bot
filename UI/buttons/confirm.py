def enroll(c_id):
    return dict(G='enroll', c_id=c_id)


def leave(c_id):
    return dict(G='leave', c_id=c_id)


def delete_course(c_id):
    return dict(G='delete_course', c_id=c_id)


def del_class(c_id, cw_id):
    return dict(G='del_class', c_id=c_id, cw_id=cw_id)


def del_task(c_id, t_id):
    return dict(G='del_task', c_id=c_id, t_id=t_id)


def kick(c_id, u_id):
    return dict(G='kick', c_id=c_id, u_id=u_id)
