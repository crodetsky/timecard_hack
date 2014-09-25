#Harvest Timecard
Quick hack to post a timecard to Harvest.

###Configuration
- Edit config.yaml and set appropriate parameters
  - Make sure to set incident_project_id, incident_task_id, automation_project_id, and automation_task_id
    - These can be acquired by setting completing today's time allocation and using harvest.get_today() then looking through the response.
- Edit weeks.yaml and set week start dates and oncall
