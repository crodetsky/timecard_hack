from harvest import Harvest
from math import floor
import json
import yaml
import random
from datetime import datetime
from datetime import timedelta

config_file = './config.yaml'
week_config = './weeks.yaml'

class Timecard():
    def __init__(self):
        self.load_config()
        self.harvest = Harvest(self.url, self.email, self.password)
        if self.oncall:
            self.hours_worked = random.randrange(self.oncall_min_hours, self.oncall_max_hours)
            self.work_sat = True
            self.work_sun = True
        else:
            self.hours_worked = random.randrange(self.min_hours, self.max_hours)
            self.work_sat = random.randrange(0,2)
            self.work_sun = random.randrange(0,2)

        self.num_days_worked = 5
        if self.work_sat:
            self.num_days_worked += 1
        if self.work_sun:
            self.num_days_worked += 1

        if self.oncall:
            self.daily_incident_hours = floor((self.hours_worked * self.oncall_incident_percent) / self.num_days_worked)
            self.daily_automation_hours = floor((self.hours_worked * (1 - self.oncall_incident_percent)) / self.num_days_worked)
        else:
            self.daily_incident_hours = floor((self.hours_worked * self.incident_percent) / self.num_days_worked)
            self.daily_automation_hours = floor((self.hours_worked * (1 - self.incident_percent)) / self.num_days_worked)

    def load_config(self):
        with open(config_file, 'r') as fd:
            config = yaml.load(fd)
        self.url = config['url']
        self.email = config['email']
        self.password = config['password']
        self.oncall = config['oncall']
        self.min_hours = config['min_hours']
        self.max_hours = config['max_hours']
        self.oncall_min_hours = config['oncall_min_hours']
        self.oncall_max_hours = config['oncall_max_hours']
        self.incident_project_id = config['incident_project_id']
        self.incident_task_id = config['incident_task_id']
        self.automation_project_id = config['automation_project_id']
        self.automation_task_id = config['automation_task_id']
        self.incident_percent = config['incident_percent']
        self.oncall_incident_percent = config['oncall_incident_percent']

    def load_weeks(self):
        with open('weeks.yaml', 'r') as fd:
            self.weeks = yaml.load(fd)

    def build_weeks(self):
        self.timecard = []
        for week in self.weeks:
            ret = {}
            if self.weeks[week]['oncall']:
                self.oncall = True
            else:
                self.oncall = False
            ret['Sunday'] = {'date': datetime.strftime(self.weeks[week]['start_date'], '%Y-%m-%d')}
            ret['Monday'] = {'date': datetime.strftime(self.weeks[week]['start_date'] + timedelta(days=1), '%Y-%m-%d')}
            ret['Tuesday'] = {'date': datetime.strftime(self.weeks[week]['start_date'] + timedelta(days=2), '%Y-%m-%d')}
            ret['Wednesday'] = {'date': datetime.strftime(self.weeks[week]['start_date'] + timedelta(days=3), '%Y-%m-%d')}
            ret['Thursday'] = {'date': datetime.strftime(self.weeks[week]['start_date'] + timedelta(days=4), '%Y-%m-%d')}
            ret['Friday'] = {'date': datetime.strftime(self.weeks[week]['start_date'] + timedelta(days=5), '%Y-%m-%d')}
            ret['Saturday'] = {'date': datetime.strftime(self.weeks[week]['start_date'] + timedelta(days=6), '%Y-%m-%d')}
            week_hours = self.build_week()
            for day in week_hours:
                ret[day]['incident_hours'] = week_hours[day]['incident_hours']
                ret[day]['automation_hours'] = week_hours[day]['automation_hours']
            self.timecard.append(ret)

    def get_hours_worked(self):
        incident_hours_worked = random.randrange((self.daily_incident_hours - 2), (self.daily_incident_hours + 2))
        automation_hours_worked = random.randrange((self.daily_automation_hours - 2), (self.daily_automation_hours + 2))
        return [incident_hours_worked, automation_hours_worked]

    def build_week(self):
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        week = {}
        for day in days:
            if day == 'Sunday':
                if self.work_sun:
                    incident_hours, automation_hours = self.get_hours_worked()
                    week[day] = {'incident_hours': incident_hours, 'automation_hours': automation_hours}
            if day == 'Saturday':
                if self.work_sat:
                    incident_hours, automation_hours = self.get_hours_worked()
                    week[day] = {'incident_hours': incident_hours, 'automation_hours': automation_hours}
            else:
                incident_hours, automation_hours = self.get_hours_worked()
                week[day] = {'incident_hours': incident_hours, 'automation_hours': automation_hours}
        return week

    def post_timecard(self):
        for week in self.timecard:
            for day in week:
                if 'incident_hours' in week[day]:
                    if week[day]['incident_hours'] != 0:
                        data = {'spent_at': week[day]['date'],
                                'hours': week[day]['incident_hours'],
                                'project_id': self.incident_project_id,
                                'task_id': self.incident_task_id}
                        response = self.harvest.add(data)
                        print json.dumps(response(), indent=4)
                if 'automation_hours' in week[day]:
                    if week[day]['automation_hours'] != 0:
                        data = {'spent_at': week[day]['date'],
                                'hours': week[day]['automation_hours'],
                                'project_id': self.automation_project_id,
                                'task_id': self.automation_task_id}
                        response = self.harvest.add(data)
                        print json.dumps(response(), indent=4)

if __name__ == '__main__':
    t = Timecard()
    t.load_weeks()
    t.build_weeks()
    print 'Posting timecard...'
    t.post_timecard()
