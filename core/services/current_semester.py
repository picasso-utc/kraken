from constance import config as live_config

def get_current_semester():
    return live_config.SEMESTER


def get_request_semester(qs, request=None):
    if request:
        semester_wanted = request.GET.get("semestre", False)
    if request and semester_wanted != False:
        if semester_wanted == "all":
            return qs.all()
        elif int(semester_wanted) > 0:
            return qs.filter(semestre__id=int(semester_wanted))
    else:
        return qs.filter(semestre__id=live_config.SEMESTER)