from django_cron import CronJobBase, Schedule
from .models import *

TAG_ID = settings.TAG_ID_LIST

class CreateMapJS(CronJobBase):
    RUN_EVERY_MINS = 60
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "core.createmapjs" # Unique code for logging purposes

    def do(self):
        import json
        items = LibraryItem.objects.filter(status="active", tags__id=TAG_ID["case_study"])
        city = {}
        all_cities = []
        for each in items:
            for space in each.spaces.all():
                if space.is_city and space.location:
                    city = {
                        "city": space.name,
                        "id": space.id, 
                        "lat": space.location.geometry.centroid[1],
                        "long": space.location.geometry.centroid[0],
                    }
                    all_cities.append(city)  
            
        all_cities = json.dumps(all_cities)
        file = settings.STATIC_ROOT + "js/librarymap.js"
        file = open(file, "w")
        file.write(all_cities)
        file.close()

class Notifications(CronJobBase):
    RUN_EVERY_MINS = 60

    def do(self):
        list = Notification.objects.filter(is_read=False).order_by("people_id")
        project = get_object_or_404(Project, pk=1)
        url_project = project.get_website()


        counter = 0
        last_people = 0
        messages_by_user = []
        url = url_project+"hub/forum/"
        for notification in list:
            print(notification.people.id)
            counter = counter + 1
            skip = False
            if counter == 1:
                skip = True

            messages_by_user.append(notification)

            if not skip and last_people != notification.people.id:
                user = notification.people.user
                context = {
                    "list": messages_by_user,
                    "firstname": user.first_name,
                    "url": url,
                    "organization_name": "Metabolism of Cities",
                }

                context = {
                    "list": messages_by_user,
                    "firstname": user.first_name,
                    "url": url,
                    "organization_name": "Metabolism of Cities",
                }

                msg_html = render_to_string("mailbody/notifications.html", context)
                msg_plain = render_to_string("mailbody/notifications.txt", context)

                sender = "Metabolismofcities" + '<info@penguinprotocols.com>'
                recipient = '"' + user.first_name + '" <' + user.email + '>'
                send_mail(
                    "Your latest notifications from The Backoffice",
                    msg_plain,
                    sender,
                    [user.email],
                    html_message=msg_html,
                )

                messages_by_user = []

            last_people = Notificationication.people.id
