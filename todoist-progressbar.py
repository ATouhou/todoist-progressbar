#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config as config
import urllib
import json
import configparser

from todoist.api import TodoistAPI
from configparser import ConfigParser

# parse config file
secrets = ConfigParser()
secrets.read('config.ini')

# read apikey form config.ini
apikey = secrets.get('config', 'apikey')
# read label_progress form config.ini
label_progress = secrets.get('config', 'label_progress')

api = TodoistAPI(apikey)
api.sync()

#print( api.state['items'])
#print( api.state['projects'])
#item = api.items.get_by_id("ID_TO_DELETE")
#item.delete()
#api.commit()


#List projects
#for project in api.state['projects']:
#    print (project['name'].encode('unicode_escape'))
#print("######\n")



#Find "progress" label id
try: 
    label_progress_id = None
    error_labelnotfound = False
    for label in api.state['labels']:
        #print(api.state['labels'])
        if label['name'] == label_progress:
            #print("progress label id =", label['id'])
            label_progress_id = label['id']
            break
    if not label_progress_id:
        error_labelnotfound = True
        raise ValueError('Label not found in Todoist. Sync skipped!')
except ValueError as error:
   print(error)


#print ("\n######\n")


#for task in api.state['items']:
#    print(sys.getsizeof(task['id']))
#    print(task['id'])
#    print(type(task['id']))
#    if isinstance(task['id'], str):
#        print("string")
#    counter = counter + 1

#print ("\n######\n")

if not error_labelnotfound:
    
    counter_progress = 0
    counter_changed_items = 0

    for task in api.state['items']:

      #if task['project_id'] == testprojekt_id:
      
        if not isinstance(task['id'], str) and task['labels'] and not task['is_deleted'] and not task['in_history'] and not task['is_archived']: 
            for label in task['labels']:
                if label == label_progress_id:
                    #print("Found task to track:", task['content'])
                    #print("content   = ", task['content']) 
                    #print("id        = ", task['id'])
                    #print("labels    = ", task['labels'])
                    #print("Order     = ", task['item_order'])
                    #print(task, "\n#####")

                    counter_progress = counter_progress + 1
                    subtasks_total = 0
                    subtasks_done = 0
                    item_order = 0
                    for subtask in api.state['items']:
                        if not subtask['content'].startswith("*"):
                            #print('Skip "text only Tasks"')
                            #print("Check for Subtasks")
                            #print("parent id = ", subtask['parent_id'])
                            #print("id of tracked task = ", task['id'])

                            if not subtask['is_deleted'] and not subtask['in_history'] and not subtask['is_archived'] and subtask['parent_id'] == task['id']:
                                #print ("### Subtask found")

                                if subtask['checked']:
                                    #print("Task is marked as done")
                                    subtasks_done = subtasks_done + 1
                                subtasks_total = subtasks_total + 1    
                        
                    if subtasks_total > 0:
                        progress_per_task = 100/subtasks_total
                    else:
                        progress_per_task = 100
                    
                    progress_done = round(subtasks_done * progress_per_task)

                    #print("Subtasks total = ", subtasks_total)
                    #print("Subtasks done = ", subtasks_done)
                    #print("\nPercent per task = ", progress_per_task)
                    #print("Percent done = ", progress_done)
                    #print ("\n######\n")
                    #print("Order in List:", task['item_order'])
                    #print(type(task['item_order']))
                    
                    item_order = task['item_order'] + 1

                    
                    item_progressbar = ""

                    if progress_done == 0:
                        item_progressbar = config.progress_bar_0
                    if progress_done > 0 and progress_done <= 20:
                        item_progressbar = config.progress_bar_20
                    if progress_done > 20 and progress_done <= 40:
                        item_progressbar =  config.progress_bar_40
                    if progress_done > 40 and progress_done <= 60:
                        item_progressbar = config.progress_bar_60
                    if progress_done > 60 and progress_done <= 80:
                        item_progressbar = config.progress_bar_80
                    if progress_done > 80 and progress_done <= 100:
                        item_progressbar = config.progress_bar_100
                    
                    progress_done = str(progress_done)

                    item_task_old = task['content']

                    if "‣" in task['content']:
                        item_content_old = task['content'].split(config.progress_seperator)
                        item_content_new = item_content_old[0]
   
                    else:
                        item_content_new = task['content'] + " "

                
                    item_content = item_content_new + "" + config.progress_seperator + " " + item_progressbar + progress_done + ' %'


                    if not item_task_old == item_content:
                        item = api.items.get_by_id(task['id'])
                        item.update(content=item_content)


                        #print(item_content)
                        #api.items.add(content=item_content, project_id=testprojekt_id , item_order= item_order, indent=2)
                        print("Changed task from:", item_task_old)
                        print("Changed task to  :", item_content)

                        #print("Sync start")
                        api.commit()       
                        print("Sync done")

                        counter_changed_items = counter_changed_items + 1
                        print("\n#####\n")




    print("\n#########\n")
    print("Tracked tasks :", counter_progress)
    print("Changed tasks :", counter_changed_items)


#Check for updates
request = urllib.request.Request(config.update_url)
try: 
    urllib.request.urlopen(request)
    
    update_releaseinforaw = urllib.request.urlopen(config.update_url).read()
    json = json.loads(update_releaseinforaw.decode('utf-8'))
    
    if not config.version == json[0]['tag_name']:
        print("\n#########\n")
        print("Your version is not up-to-date!")
        print("Your version  :" , config.version)
        print("Latest version: ", json[0]['tag_name'])
        print("See latest version at: ", json[0]['html_url'])
        print("\n#########")

except urllib.error.URLError as e:
   print("Error while checking for updates: ", e.reason)
except urllib.error.HTTPError as e:
   print("Error while checking for updates: ", e.code)

print("\nEnd")


