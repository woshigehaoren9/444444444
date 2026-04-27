from datetime import datetime
import time

#find the course  attend
def find_current_course(tableDict):
    have_class = 0
    course_name = None
    classroom = None
    start_time = None
    end_time =None
    late = 0

    current_time = datetime.now().strftime("%H:%M")
    current_week = int(time.strftime("%w"))
    current_week_key = list(tableDict.keys())[current_week - 1]
    today_course = tableDict[current_week_key]
    if current_week in [0,6]:
        print("None")
        return have_class,course_name,classroom,start_time,end_time,late
    else:
        print(today_course)
        min_diff_time = 24 * 60
        for course in today_course:
            if course != []:
                if in_course_time(course[2],course[3],current_time):
                    print(in_course_time(course[2],course[3],current_time))
                    have_class = 1
                    course_name = course[0]
                    classroom = course[1]
                    start_time = course[2]
                    end_time = course[3]
                    late = 1
                    return have_class,course_name,classroom,start_time,end_time,late
                else:
                    current_diff_time = diff_time(course[2],current_time)
                    if current_diff_time <= 0 and current_diff_time < min_diff_time:
                        min_diff_time = current_diff_time
                        print("min_time:{}".format(min_diff_time))
                        have_class = 1
                        course_name = course[0]
                        classroom = course[1]
                        start_time = course[2]
                        end_time = course[3]
                        late = 0
                        return have_class, course_name, classroom, start_time, end_time, late
        print("None")
        return have_class, course_name, classroom, start_time, end_time, late
    print(current_time)
    print(current_week)

# the difference of two time
def diff_time(time1,time2):
    t1,m1 = int(time1.split(':')[0]), int(time1.split(':')[1])
    t2, m2 = int(time2.split(':')[0]), int(time2.split(':')[1])
    time1_min = t1 * 60 + m1
    time2_min = t2 * 60 + m2
    return time2_min - time1_min

#current time is in course time?
def in_course_time(start_time,end_time,current_time):
    if diff_time(start_time,current_time) > 0 and diff_time(end_time,current_time) < 0:
        return True
    else:
        return False

