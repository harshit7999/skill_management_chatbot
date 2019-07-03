from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Employee,Department,Skill,SkillLevel,SkillGroup,EmployeeSkillList
from django.conf import settings 

def SimpleResponse(response,suggestion=[],context=[],expectUserResponse=True):
    settings.json_data_simple_response['payload']["google"]["richResponse"]["items"][0]["simpleResponse"]["textToSpeech"] = response
    settings.json_data_simple_response['payload']["google"]["richResponse"]["items"][0]["simpleResponse"]["displayText"] = response
    settings.json_data_simple_response["outputContexts"] = context
    settings.json_data_simple_response['payload']['google']['richResponse']['suggestions'] = suggestion
    settings.json_data_simple_response['payload']['google']['expectUserResponse'] = expectUserResponse
    json.dumps(settings.json_data_simple_response)
    return settings.json_data_simple_response

def TableCard(response,row_column_list,suggestion=[],context=[],expectUserResponse=True):
    settings.json_data_table_card['payload']["google"]["richResponse"]["items"][0]["simpleResponse"]["textToSpeech"] = response
    settings.json_data_table_card['payload']["google"]["richResponse"]["items"][0]["simpleResponse"]["displayText"] = response
    settings.json_data_table_card["outputContexts"] = context
    settings.json_data_table_card['payload']['google']['richResponse']['suggestions'] = suggestion
    settings.json_data_table_card['payload']['google']['expectUserResponse'] = expectUserResponse
    settings.json_data_table_card['payload']["google"]["richResponse"]["items"][1]["tableCard"]["rows"]=row_column_list[0]
    settings.json_data_table_card['payload']["google"]["richResponse"]["items"][1]["tableCard"]["columnProperties"]=row_column_list[1]
    json.dumps(settings.json_data_table_card)
    return settings.json_data_table_card

def ListResponse(response,items,suggestion=[],context=[],expectUserResponse=True):
    settings.json_data_list_response['payload']["google"]["richResponse"]["items"][0]["simpleResponse"]["textToSpeech"] = response
    settings.json_data_list_response['payload']["google"]["richResponse"]["items"][0]["simpleResponse"]["displayText"] = response
    settings.json_data_list_response["outputContexts"] = context
    settings.json_data_list_response['payload']['google']['richResponse']['suggestions'] = suggestion
    settings.json_data_list_response['payload']['google']['expectUserResponse'] = expectUserResponse
    settings.json_data_list_response['payload']["google"]["systemIntent"]["data"]["listSelect"]["items"]=items
    json.dumps(settings.json_data_list_response)
    return settings.json_data_list_response

def get_current_skillset():
    row=[]
    column=[{"header": "Skill Name"},{"header": "Skill Level"}]
    for current_element in EmployeeSkillList.objects.filter(employee=settings.emp):
      row.append({"cells":[{"text":current_element.skill.skill_name},{"text":current_element.skill_level.skill_level_name}]})
    return [row,column] 

def get_employee_list(employee_list,skill_list):    
    row=[]
    row_inner=[]
    column=[{"header": "Employee"}]
    for current_element_skill in skill_list:
      column.append({"header": current_element_skill.skill_name})
    for current_element_employee in employee_list:
      row_inner.append({"text":current_element_employee.employee_name})
      for current_element_skill in skill_list:
        row_inner.append({"text":EmployeeSkillList.objects.get(employee=current_element_employee,skill=current_element_skill).skill_level.skill_level_name})
      row.append({"cells":row_inner})
      row_inner=[]
    return [row,column]

def get_yes_no_suggestion():
    return [{'title':'yes'},{'title':'no'},]

def get_context(context_name,context_lifespan,session):
    for context_number in range(len(context_name)):
      context_name[context_number] = ({"name":session+"/contexts/"+context_name[context_number],"lifespanCount": context_lifespan[context_number]})
    return context_name

def call_event(event_name,parameters={}):
    data = {"followupEventInput":{  
              "name":event_name,
              "parameters":parameters
              }
            }
    return data

@csrf_exempt
def webhook(request):
    req = json.loads(request.body)
    action = req.get('queryResult').get('action')

    if action == "WelcomeSudo":
        settings.sk_string = ""
        settings.sk_name = ""
        settings.emp_sk_list = []
        settings.emp = Employee.objects.get(id=4)
        settings.skills_searched=[]
        settings.session = req.get('session')
        json_file=open('RichResponses/SimpleResponse.json',"r")
        settings.json_data_simple_response=json.load(json_file)
        json_file.close()
        json_file=open('RichResponses/TableCard.json',"r")
        settings.json_data_table_card=json.load(json_file)
        json_file.close()
        json_file=open('RichResponses/ListResponse.json',"r")
        settings.json_data_list_response=json.load(json_file)
        json_file.close()
        data = call_event('Welcome')
        return JsonResponse(data,safe=False)

    elif action=="input.welcome":
        #items=[{"optionInfo": {"key":"update"},"description": "Update your skill-set","title": "Update"},{"optionInfo": {"key":"Search Employees"},"description": "You can also type {search employees with <skill-name> skill}.","title": "Search Employees"},]
        data = SimpleResponse("Hey! How can I help you?"+"\n"+"- update your skill-set"+"\n"+"-search employees (one skill at a time)",[{'title':'update'},{'title':'search employees'}],get_context(['UpdateSkillSet','Welcome'],[1,0],settings.session))
        #data = ListResponse("Hi! Welcome to Skill Management Chatbot"+'\n'+"How may I help you?",items,[],get_context(['UpdateSkillSet','Welcome'],[1,0],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "DefaultWelcomeIntent-fallback":
        #items=[{"optionInfo": {"key":"update"},"description": "Update your skill-set","title": "Update"},{"optionInfo": {"key":"Search Employees"},"description": "You can also type {search employees with <skill-name> skill}.","title": "Search Employees"},]
        data = SimpleResponse("Please enter a valid response"+"\n"+"How can I help you?"+"\n"+"- update your skill-set"+"\n"+"-search employees",[{'title':'update'},],get_context(['UpdateSkillSet'],[1],settings.session))
        #data = ListResponse("Please enter a valid response."+'\n'+"How may I help you?",items,[],get_context(['UpdateSkillSet'],[1],settings.session))        
        return JsonResponse(data,safe=False)     

    elif action == "UpdateSkillSet":
        data = TableCard("Your current skill-set is given below."+'\n'+"Do you want update level of any of your existing skill?",get_current_skillset(),get_yes_no_suggestion(),get_context(['UpdateSkillSet-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "UpdateSkillSet-yes":
        items=[]
        for current_element in EmployeeSkillList.objects.filter(employee=settings.emp):
          items.append({"optionInfo": {"key":current_element.skill.skill_name},"description": current_element.skill_level.skill_level_name,"title": current_element.skill.skill_name},)
        data=ListResponse("Select the skill whose level you want to update from the list given below OR type the name of the skill",items,[],get_context(['UpdateSkillSet-yes-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "UpdateSkillSet-fallback":
        data = SimpleResponse("Please enter a valid response"+"\n"+"Do you want to update the level of your existing skill?",get_yes_no_suggestion(),get_context(['UpdateSkillSet-followup'],[1],settings.session))
        return JsonResponse(data,safe=False) 

    elif action == "UpdateSkillSet-yes-custom":
        settings.sk_name=req.get("originalDetectIntentRequest").get("payload").get("inputs")[0].get("arguments")[0].get("textValue")
        if Skill.objects.filter(skill_name=settings.sk_name).exists()==False or Skill.objects.get(skill_name=settings.sk_name).employeeskilllist_set.filter(employee=settings.emp).exists()==False:
          data=call_event("UpdateSkillSet-yes-custom-custom-2")
          return JsonResponse(data,safe=False)
        else:
          suggestion=[]
          for current_element in SkillLevel.objects.all():
            if current_element != EmployeeSkillList.objects.get(employee=settings.emp,skill=Skill.objects.get(skill_name=settings.sk_name)).skill_level:
              suggestion.append({'title':current_element.skill_level_name})
          data = SimpleResponse("Your current level of "+settings.sk_name+" is "+EmployeeSkillList.objects.get(employee=settings.emp,skill=Skill.objects.get(skill_name=settings.sk_name)).skill_level.skill_level_name+"."+'\n'+"What is the new skill level of skill "+settings.sk_name+" ?",suggestion,get_context(['UpdateSkillSet-yes-custom-followup'],[1],settings.session))
          return JsonResponse(data,safe=False)
       
    elif action == "UpdateSkillSet-yes-custom-custom-2":
        data = SimpleResponse("The Skill you entered does not exist in your skill-set."+'\n'+" Do you want to add "+settings.sk_name +" it to your skill-set?",get_yes_no_suggestion(),get_context(['UpdateSkillSet-yes-custom-custom-2-followup'],[1],settings.session))
        return JsonResponse(data,safe=False) 

    elif action == "UpdateSkillSet-yes-custom-custom-2-no":
        data = SimpleResponse("No cahnges have been made to your skill-set. "+'\n'+'Do you want to update level of any other existing skill?',get_yes_no_suggestion(),get_context(['UpdateSkillSet-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == 'UpdateSkillSet-yes-custom-custom-2-fallback':
        data = SimpleResponse("Please enter a valid response (yes/no)."+'\n'+"Do you want to add skill"+settings.sk_name+" to your skill-set?",get_yes_no_suggestion(),get_context(['UpdateSkillSet-yes-custom-custom-2-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "UpdateSkillSet-yes-custom-custom-2-yes":       
        if Skill.objects.filter(skill_name=settings.sk_name).exists()==False:
          data = call_event('UpdateSkillSet-yes-custom-custom-2-yes-custom')
          return JsonResponse(data,safe=False)
        else:
          EmployeeSkillList(employee=settings.emp,skill=Skill.objects.get(skill_name=settings.sk_name),skill_level=SkillLevel.objects.get(skill_level_name="Beginner")).save()
        response = "You updated skill-set is:"+'\n'
        for current_element in EmployeeSkillList.objects.filter(employee=settings.emp):
          response = response + current_element.skill.skill_name + " - " + current_element.skill_level.skill_level_name + '\n'
        data = SimpleResponse("The skill "+settings.sk_name+" has been added to your skill-set at beginner level."+'\n'+response+'\n'+"Do you want to change level of any other existing skill ?",get_yes_no_suggestion(),get_context(['UpdateSkillSet-followup','UpdateSkillSet-yes-custom-custom-2-yes-followup'],[1,0],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "UpdateSkillSet-yes-custom-custom-2-yes-custom":
      items=[]
      for current_element in SkillGroup.objects.all():
        items.append({"optionInfo": {"key":str(current_element.skill_group_no)},"description":current_element.skill_group_name ,"title": str(current_element.skill_group_no)},)
      data = ListResponse("As "+settings.sk_name+" does not exist in database, in order to add it to databse choose an appropriate skill group for the skill. A list of skill group number and skill group name is given below.",items,[],get_context(['UpdateSkillSet-yes-custom-custom-2-yes-custom-followup'],[1],settings.session))
      return JsonResponse(data,safe=False)

    elif action == "UpdateSkillSet-yes-custom-custom":
        settings.new_level = req.get('queryResult').get('parameters').get('SkillLevel')
        employee_skill_list_row_to_be_changed = EmployeeSkillList.objects.get(employee=settings.emp,skill=Skill.objects.get(skill_name=settings.sk_name.lower()))
        settings.current_level = employee_skill_list_row_to_be_changed.skill_level.skill_level_name
        if (settings.current_level=="Beginner" and settings.new_level=="Intermediate") or (settings.new_level=="Advance" and settings.current_level=="Intermediate") or (settings.new_level==settings.current_level): 
          row=[]
          column=[{"header": "Skill Name"},{"header": "Skill Level"}]
          employee_skill_list_row_to_be_changed.skill_level=SkillLevel.objects.get(skill_level_name=settings.new_level)
          employee_skill_list_row_to_be_changed.save()
          for current_element in EmployeeSkillList.objects.filter(employee=settings.emp):
            row.append({"cells":[{"text":current_element.skill.skill_name},{"text":current_element.skill_level.skill_level_name}]})
          data = TableCard("Your skill-set is updated. "+'\n'+"Do you want update level of any of your existing skill?",get_current_skillset(),get_yes_no_suggestion(),get_context(['UpdateSkillSet-followup','UpdateSkillSet-yes-custom-custom-followup'],[1,0],settings.session))
          return JsonResponse(data,safe=False)
        else:
          data = SimpleResponse("Are you sure you want to update "+settings.sk_name+"'s level from "+settings.current_level+" to "+settings.new_level+"?",get_yes_no_suggestion(),get_context(['UpdateSkillSet-followup','UpdateSkillSet-yes-custom-custom-followup'],[0,1],settings.session))
          return JsonResponse(data,safe=False)

    elif action == "UpdateSkillSet-yes-custom-custom-fallback":
        data = SimpleResponse("Please enter a valid response.(Yes/No) "+'\n'+ 'Are you sure you want to update '+settings.sk_name+"'s level from "+settings.current_level+" to "+settings.new_level+" ?",get_yes_no_suggestion(),get_context(['UpdateSkillSet-yes-custom-custom-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "UpdateSkillSet-yes-custom-fallback":
        suggestion=[]
        for current_element in SkillLevel.objects.all():
          if current_element != EmployeeSkillList.objects.get(employee=settings.emp,skill=Skill.objects.get(skill_name=settings.sk_name)).skill_level:
            suggestion.append({'title':current_element.skill_level_name})
        data = SimpleResponse("Please enter a valid response"+'\n'+"Your current level of "+settings.sk_name+" is "+EmployeeSkillList.objects.get(employee=settings.emp,skill=Skill.objects.get(skill_name=settings.sk_name)).skill_level.skill_level_name+"."+'\n'+"What is the new skill level of "+settings.sk_name+'?',suggestion,get_context(['UpdateSkillSet-yes-custom-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "UpdateSkillSet-yes-custom-custom-yes":
        employee_skill_list_row_to_be_changed = EmployeeSkillList.objects.get(employee=settings.emp,skill=Skill.objects.get(skill_name=settings.sk_name.lower()))
        employee_skill_list_row_to_be_changed.skill_level = SkillLevel.objects.get(skill_level_name=settings.new_level)
        employee_skill_list_row_to_be_changed.save()
        data = TableCard("Your skill-set has been updated "+'\n'+"Do you want update level of any of your existing skill?",get_current_skillset(),get_yes_no_suggestion(),get_context(['UpdateSkillSet-followup'],[1],settings.session)) 
        return JsonResponse(data,safe=False)

    elif action == "UpdateSkillSet-yes-custom-custom-no":
        data = SimpleResponse("No changes have been made to your skill-set."+'\n'+"Do you want to update level of any other existing skill?",get_yes_no_suggestion(),get_context(['UpdateSkillSet-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "UpdateSkillSet-yes-custom-custom-2-yes-custom-custom":
        group_number_as_parameter = int(req.get("originalDetectIntentRequest").get("payload").get("inputs")[0].get("arguments")[0].get("textValue"))
        if SkillGroup.objects.filter(skill_group_no=group_number_as_parameter).exists() == True:
          Skill(skill_name=settings.sk_name.lower(),skill_group=SkillGroup.objects.get(skill_group_no=group_number_as_parameter)).save()
          EmployeeSkillList(employee=settings.emp,skill=Skill.objects.get(skill_name=settings.sk_name.lower()),skill_level=SkillLevel.objects.get(skill_level_name='Beginner')).save()
          data = TableCard("SKill " + settings.sk_name + " has been added to your skill-set at Beginner level " + '\n' + "Your updated skill-set is given below."+ '\n'+"Do you want update level of any of your existing skill?",get_current_skillset(),get_yes_no_suggestion(),get_context(['UpdateSkillSet-followup','UpdateSkillSet-yes-custom-custom-2-yes-custom-followup'],[1,0],settings.session)) 
          return JsonResponse(data,safe=False)
        else:
          data = call_event('UpdateSkillSet-yes-custom-custom-2-yes-custom-fallback')
          return JsonResponse(data,safe=False)

    elif action == "UpdateSkillSet-yes-custom-custom-2-yes-custom-fallback":
        items=[]
        for current_element in SkillGroup.objects.all():
          items.append({"optionInfo": {"key":str(current_element.skill_group_no)},"description":current_element.skill_group_name ,"title": str(current_element.skill_group_no)},)
        data = ListResponse("The skill Group number you entered does not exist. "+'\n'+ "please enter a valid skill group number to which you want to add skill "+settings.sk_name,items,[],get_context(['UpdateSkillSet-yes-custom-custom-2-yes-custom-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "UpdateSkillSet-no":
        data = SimpleResponse("Do you want to add a new skill to your skill-set?",get_yes_no_suggestion(),get_context(['UpdateSkillSet-no-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "UpdateSkillSet-no-no":
        data = SimpleResponse("Thank You! Good Bye.",[],[],False)
        return JsonResponse(data,safe=False)

    elif action == "UpdateSkillSet-no-fallback":
        data = SimpleResponse("Please enter valid response (Yes/No)."+'\n'+"Do you want to add a new skill to your skill set?",get_yes_no_suggestion(),get_context(['UpdateSkillSet-no-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "UpdateSkillSet-no-yes":
        suggestion = []
        for current_element in Skill.objects.all():
          if EmployeeSkillList.objects.filter(employee=settings.emp,skill=current_element).exists()==False:
            suggestion.append({'title':current_element.skill_name})
        data = SimpleResponse("Which new skill you want to add to your skill-set?",suggestion,get_context(['UpdateSkillSet-no-yes-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)
    
    elif action == "UpdateSkillSet-no-yes-custom":
        settings.sk_name = req.get('queryResult').get('parameters').get('any').lower()
        if Skill.objects.filter(skill_name=settings.sk_name.lower()).exists()==False:
          response = ""
          suggestion=[]
          for current_element in SkillGroup.objects.all():
            response = response+str(current_element.skill_group_no)+" "+current_element.skill_group_name+'\n'
            suggestion.append({'title':str(current_element.skill_group_no)})
          data = SimpleResponse("As "+settings.sk_name+" does not exist in the database, please provide a valid group number to the skill from the options given below in order to add "+settings.sk_name+" to your skill set."+'\n'+response,suggestion,get_context(['UpdateSkillSet-no-followup','UpdateSkillSet-no-yes-custom-followup'],[0,1],settings.session))
          return JsonResponse(data,safe=False)
        elif Skill.objects.filter(skill_name=settings.sk_name.lower()).exists()==True and EmployeeSkillList.objects.filter(employee=settings.emp,skill=Skill.objects.get(skill_name=settings.sk_name.lower())).exists()==False:
          EmployeeSkillList(employee=settings.emp,skill=Skill.objects.get(skill_name=settings.sk_name),skill_level=SkillLevel.objects.get(skill_level_name="Beginner")).save()
          data = TableCard("Skill "+settings.sk_name+" has been added to your skillset at Beginner level."+'\n'+"Your updated skill-set is given below. "+ '\n'+"Do you want update level of any of your existing skill?",get_current_skillset(),get_yes_no_suggestion(),get_context(['UpdateSkillSet-no-followup','UpdateSkillSet-no-yes-custom-followup'],[1,0],settings.session)) 
          return JsonResponse(data,safe=False)
        else:
          data = SimpleResponse("Skill "+settings.sk_name+" already exist in skill-set."+'\n'+'Do you want to add any other skill?',get_yes_no_suggestion(),get_context(['UpdateSkillSet-no-followup','UpdateSkillSet-no-yes-custom-followup'],[1,0],settings.session))
          return JsonResponse(data,safe=False)
        
    elif action == "UpdateSkillSet-no-yes-custom-custom":
        group_number_as_parameter = int(req.get('queryResult').get('parameters').get('number'))
        if SkillGroup.objects.filter(skill_group_no=group_number_as_parameter).exists()==True:
          Skill(skill_name=settings.sk_name.lower(),skill_group=SkillGroup.objects.get(skill_group_no=group_number_as_parameter)).save()
          EmployeeSkillList(employee=settings.emp,skill=Skill.objects.get(skill_name=settings.sk_name.lower()),skill_level=SkillLevel.objects.get(skill_level_name="Beginner")).save()
          data = TableCard("Skill "+settings.sk_name+" has been added to your skillset at Beginner level."+'\n'+"Your updated skill-set is given below. "+ '\n'+"Do you want update level of any of your existing skill?",get_current_skillset(),get_yes_no_suggestion(),get_context(['UpdateSkillSet-no-followup'],[1],settings.session))
          return JsonResponse(data,safe=False)
        else:
          data = call_event('UpdateSkillSet-no-yes-custom-fallback')
          return JsonResponse(data,safe=False)
          
    elif action == "UpdateSkillSet-no-yes-custom-fallback":
        suggestion = []
        for current_element in SkillGroup.objects.all():
          suggestion.append({'title':str(current_element.skill_group_no)})
        data = SimpleResponse("Please enter a valid skill group number to which you want to add skill "+settings.sk_name,suggestion,get_context(['UpdateSkillSet-no-yes-custom-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "SearchEmployees": 
        settings.sk_name = req.get('queryResult').get('parameters').get('any').lower()
        if Skill.objects.filter(skill_name=settings.sk_name).exists()==True:
          response = ""
          for current_element in EmployeeSkillList.objects.filter(skill=Skill.objects.get(skill_name=settings.sk_name)):
            settings.emp_sk_list.append(current_element.employee)
          if len(EmployeeSkillList.objects.filter(skill=Skill.objects.get(skill_name=settings.sk_name)))>0:
            if Skill.objects.get(skill_name=settings.sk_name.lower()) not in settings.skills_searched:
              settings.sk_string = settings.sk_string + " " + settings.sk_name
              settings.skills_searched.append(Skill.objects.get(skill_name=settings.sk_name.lower()))
            data = TableCard("List of employees with skill: "+settings.sk_string+'\n'+"Do you want to filter more?",get_employee_list(settings.emp_sk_list,settings.skills_searched),get_yes_no_suggestion(),get_context(['SearchEmployees-followup'],[1],settings.session))
            return JsonResponse(data,safe=False)
          else:
            alternate_skill_count = 0
            for current_element in Skill.objects.get(skill_name=settings.sk_name).skill_group.skill_set.all():
              if current_element.skill_name!=settings.sk_name.lower() and len(current_element.employeeskilllist_set.all())>0:
                alternate_skill_count = alternate_skill_count + 1
            if alternate_skill_count>0:
              data = SimpleResponse("There are no employees with skill "+settings.sk_name+'\n'+"Do you want to search employees on basis of any alternate skill in the same group as "+settings.sk_name+"?",get_yes_no_suggestion(),get_context(['Alternate','SearchEmployees-followup'],[1,0],settings.session))
              return JsonResponse(data,safe=False)
            else:
              data = SimpleResponse("There are no employees with skill "+settings.sk_name+'\n'+"Do you want to start search again? ",get_yes_no_suggestion(),get_context(['StartSearchAgain','SearchEmployees-followup'],[1,0],settings.session))
              return JsonResponse(data,safe=False)
        else:
          data = SimpleResponse("Skill "+settings.sk_name+" does not exist in database."+'\n'+"Do you want to start search again?",get_yes_no_suggestion(),get_context(['StartSearchAgain','SearchEmployees-followup'],[1,0],settings.session))
          return JsonResponse(data,safe=False)
  
    elif action == "SearchEmployees-fallback":
        data = SimpleResponse("Please enter a valid response."+'\n'+"Do you want to filter more (Yes/No)?",get_yes_no_suggestion(),get_context(['SearchEmployees-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "SearchEmployees-no":
        data = SimpleResponse("Do you want to start search again?",get_yes_no_suggestion(),get_context(['StartSearchAgain'],[1],settings.session))
        return JsonResponse(data,safe=False)   
    
    elif action == "SearchEmployees-yes":
        suggestion = []
        for current_element in Skill.objects.filter(skill_group=Skill.objects.get(skill_name=settings.sk_name.lower()).skill_group):
          if current_element not in settings.skills_searched:
            suggestion.append({'title':current_element.skill_name})
        data = SimpleResponse("Enter other skill (one skill at a time)",suggestion,get_context(['SearchEmployees-yes-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)
    
    elif action == "SearchEmployees-yes-custom":
        settings.sk_name = req.get('queryResult').get('parameters').get('any').lower()
        if Skill.objects.filter(skill_name=settings.sk_name.lower()).exists():
          new_emp_sk_list = []
          for current_element in EmployeeSkillList.objects.filter(skill=Skill.objects.get(skill_name=settings.sk_name)):
            if current_element.employee in settings.emp_sk_list:
              new_emp_sk_list.append(current_element.employee)
          settings.emp_sk_list = new_emp_sk_list
          if Skill.objects.get(skill_name=settings.sk_name.lower()) not in settings.skills_searched:
            settings.sk_string = settings.sk_string + ", " + settings.sk_name
            settings.skills_searched.append(Skill.objects.get(skill_name=settings.sk_name))
          if len(settings.emp_sk_list)>0:
            data = TableCard("List of employees with skills: "+settings.sk_string+'\n'+"Do you want to filter more?", get_employee_list(settings.emp_sk_list,settings.skills_searched),get_yes_no_suggestion(),get_context(['SearchEmployees-yes-custom-followup'],[1],settings.session))
            return JsonResponse(data,safe=False)
          else:
            data = SimpleResponse("List of employees with skills: "+settings.sk_string+'\n'+"No such employee exist. "+'\n'+"Do you want to start search again?",get_yes_no_suggestion(),get_context(['StartSearchAgain'],[1],settings.session))
            return JsonResponse(data,safe=False)
        else:
          data = SimpleResponse("Skill "+settings.sk_name+" does not exist in databse."+'\n'+"Do you want to start search again?",get_yes_no_suggestion(),get_context(['StartSearchAgain'],[1],settings.session))
          return JsonResponse(data,safe=False)
        
    elif action == "SearchEmployees-yes-custom-yes":
        data = call_event('SearchEmployees-yes')
        return JsonResponse(data,safe=False)

    elif action == "SearchEmployees-yes-custom-no":
        data = call_event('SearchEmployees-no')
        return JsonResponse(data,safe=False)

    elif action == "SearchEmployees-yes-custom-fallback":
        data = SimpleResponse("Please enter a valid response."+'\n'+"Do you want to filter more (Yes/No)?",get_yes_no_suggestion(),get_context(['SearchEmployees-yes-custom-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "Alternate_fallback":
        data = SimpleResponse("Please enter a valid response."+'\n'+"Do you want to search employee on basis of an alternate skill (Yes/No)?",get_yes_no_suggestion(),get_context(['Alternate'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "Alternate_yes":
        items = []
        for current_element in Skill.objects.get(skill_name=settings.sk_name).skill_group.skill_set.all():
          if current_element.skill_name!=settings.sk_name.lower() and len(current_element.employeeskilllist_set.all())>0:
            items.append({"optionInfo": {"key":current_element.skill_name},"description":"","title": current_element.skill_name},)
        data = ListResponse("Select a skill from the list given below: ",items,[],get_context(['Alternate_yes-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "Alternate_yes-custom":
        sk_name_1 = req.get("originalDetectIntentRequest").get("payload").get("inputs")[0].get("arguments")[0].get("textValue")
        if sk_name_1.lower()==settings.sk_name.lower() or Skill.objects.filter(skill_name=sk_name_1.lower()).exists()==False or Skill.objects.get(skill_name=sk_name_1).skill_group.skill_group_no!=Skill.objects.get(skill_name=settings.sk_name).skill_group.skill_group_no:
          items=[]
          for current_element in Skill.objects.get(skill_name=settings.sk_name).skill_group.skill_set.all():
            if current_element.skill_name!=settings.sk_name.lower() and len(current_element.employeeskilllist_set.all())>0:
              items.append({"optionInfo": {"key":current_element.skill_name},"description":"","title": current_element.skill_name},)
          data = ListResponse("You didn't entered a skill from the list provided."+'\n'+"Please select a skill from the list provided below: ",items,[],get_context(['Alternate_yes-followup'],[1],settings.session))
          return JsonResponse(data,safe=False)
        else:
          for current_element in EmployeeSkillList.objects.filter(skill=Skill.objects.get(skill_name=sk_name_1)):
            settings.emp_sk_list.append(current_element.employee)
          if Skill.objects.get(skill_name=sk_name_1.lower()) not in settings.skills_searched:
            settings.sk_string = settings.sk_string + sk_name_1
            settings.skills_searched.append(Skill.objects.get(skill_name=sk_name_1.lower()))
          data = TableCard("List of employees with skill: "+settings.sk_string+'\n'+"Do you want to filter more?",get_employee_list(settings.emp_sk_list,settings.skills_searched),get_yes_no_suggestion(),get_context(['SearchEmployees-followup'],[1],settings.session))
          return JsonResponse(data,safe=False)

    elif action == "Alternate_no":
        data = SimpleResponse("Do you want to start search again?",get_yes_no_suggestion(),get_context(['StartSearchAgain'],[1],settings.session))
        return JsonResponse(data,safe=False)
    
    elif action == "Alternate_no-no" or action=="StartSearchAgain_no":
        data = SimpleResponse("Thank you! Good Bye.",[],[],False)
        return JsonResponse(data,safe=False)
  
    elif action == "StartSearchAgain_fallback":
        data = SimpleResponse("Please enter a valid response"+'\n'+"Do you want to start search again (Yes/No)?",get_yes_no_suggestion(),get_context(['StartSearchAgain'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "StartSearchAgain_yes":
        settings.emp_sk_list = []
        settings.sk_string = ""
        settings.skills_searched=[]
        suggestion=[]
        for current_element in Skill.objects.all():
          suggestion.append({'title':current_element.skill_name})
        data = SimpleResponse("Enter skill name (one skill at a time)",suggestion,get_context(['StartSearchAgain_yes-followup'],[1],settings.session))
        return JsonResponse(data,safe=False)

    elif action == "StartSearchAgain_yes-custom":
        skill_name_as_parameter = req.get('queryResult').get('parameters').get('any')
        data = call_event('SearchEmployees',{'any':skill_name_as_parameter})
        return JsonResponse(data,safe=False)



        

        






              
            

                  
        
          

      


          

      

    






    
        

          
    
        


