def enroll(course_id):
    return dict(goto='enroll', course_id=course_id)


def leave(course_id):
    return dict(goto='leave', course_id=course_id)


def delete_course(course_id):
    return dict(goto='delete_course', course_id=course_id)
