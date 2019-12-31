from constance import config as live_config

def get_current_semester():
    return live_config.SEMESTER


def get_request_semester(qs, request=None, attribute=None):
    if not attribute:
        attribute = "semestre__id"
    if request:
        semester_wanted = request.GET.get("semestre", False)
    if request and semester_wanted != False:
        if semester_wanted == "all":
            return qs.all()
        elif int(semester_wanted) > 0:
            return qs.filter(**{attribute: int(semester_wanted)})
            
    else:
        return qs.filter(**{attribute: live_config.SEMESTER})