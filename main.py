import sys
from decouple import config
import requests
from zenpy import Zenpy

ZENDESK_EMAIL = config('ZENDESK_EMAIL', '')
ZENDESK_PASSWORD = config('ZENDESK_PASSWORD', '')
ZENDESK_DOMAIN = config('ZENDESK_DOMAIN', '')
ZENDESK_BASICAUTH = config('ZENDESK_BASICAUTH', '')
ZENDESK_URL = config('ZENDESK_URL', '')

def get_zempy_conexao():
    creds = {
        'email': ZENDESK_EMAIL,
        'token': ZENDESK_PASSWORD,
        'subdomain': ZENDESK_DOMAIN,
    }
    session = requests.Session()
    zenpy_client = Zenpy(**creds, session=session)

    return zenpy_client

def main():
    ticketid = 2425717#2420520#1134721
    zenpy_client = get_zempy_conexao()

    # ticket = zenpy_client.tickets(id=ticketid)
    # print(ticket.custom_fields)

    tickets_custom_fields = None
    tickets_ticket_form = None
    tickets_agent_conditions = None
    tickets_ticket_fields = None

    url = f"{ZENDESK_URL}/api/v2/tickets/{ticketid}.json?include=users,brands"
    payload = {}
    headers = {
        'Authorization': ZENDESK_BASICAUTH,
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    # print(response.json()["ticket"]["ticket_form_id"])
    tickets_custom_fields = response.json()["ticket"]["custom_fields"]
    ticket_form_id = response.json()["ticket"]["ticket_form_id"]

    url = f"{ZENDESK_URL}/api/v2/ticket_forms/{ticket_form_id}.json?include=ticket_fields"
    payload = {}
    headers = {
        'Authorization': ZENDESK_BASICAUTH,
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    # for x in response.json()["ticket_fields"]:
    #     print(x["title"])
    # print(response.json()["ticket_fields"][0]["title"])
    tickets_ticket_form = response.json()["ticket_form"]
    tickets_ticket_fields = response.json()["ticket_fields"]
    tickets_agent_conditions = response.json()["ticket_form"]["agent_conditions"]
    tickets_ticket_field_ids = response.json()["ticket_form"]["ticket_field_ids"]

    for agent_conditions in tickets_agent_conditions:
        if len(agent_conditions["child_fields"]) > 0:
            for child_fields in agent_conditions["child_fields"]:
                # print(child_fields["is_required"])
                pass
    
    fields_conditions = []
    for custom_fields in tickets_custom_fields:
        if not custom_fields["id"] in tickets_ticket_form["ticket_field_ids"]:
            continue
        for ticket_fields in tickets_ticket_fields:
            if not custom_fields["id"] == ticket_fields["id"]:
                continue
            # if "priority" in ticket_fields["type"]:
            #     print(ticket_fields["title"])
            # print(ticket_fields["title"], ticket_fields["id"])

        
        for agent_conditions in tickets_agent_conditions:
            if not custom_fields["id"] == agent_conditions["parent_field_id"]:
                continue
            if not custom_fields["value"] == agent_conditions["value"]:
                continue
            print(agent_conditions["parent_field_id"], agent_conditions["value"])
            if agent_conditions["value"] is None:
                continue
            if len(agent_conditions["value"]) == 0:
                continue
            if agent_conditions["value"] == "":
                continue
            
            
            # url = f"https://grupocard.zendesk.com/api/v2/ticket_fields/{agent_conditions['parent_field_id']}/options"
            # payload = {}
            # headers = {
            #     'Authorization': ZENDESK_BASICAUTH,
            # }
            # response = requests.request("GET", url, headers=headers, data=payload)
            # pular = False
            # for custom_field_options in response.json()["custom_field_options"]:
            #     if custom_field_options["value"] == agent_conditions["value"]:
            #         pular = True
            # if pular:
            #     continue
            
            # print(agent_conditions)
            if not agent_conditions['parent_field_id'] in fields_conditions:
                fields_conditions.append(agent_conditions['parent_field_id'])
            for child_fields in agent_conditions['child_fields']:
                if child_fields['id'] in fields_conditions:
                    continue
                # if "ALL_STATUSES" in child_fields['required_on_statuses']['type']:
                #     continue
                # if "SOME_STATUSES" in child_fields['required_on_statuses']['type']:
                #     continue
                fields_conditions.append(child_fields['id'])
    print("campos: ", fields_conditions, len(fields_conditions))

    print("\n FIELD   |   VALOR")
    for custom_fields in tickets_custom_fields:
        if custom_fields["id"] in fields_conditions:
            print(custom_fields["id"], custom_fields["value"])

    # lista de formularios
    print("\n- lista de formularios")
    url = f"{ZENDESK_URL}/api/v2/ticket_forms"
    payload = {}
    headers = {
        'Authorization': ZENDESK_BASICAUTH,
    }
    # response = requests.request("GET", url, headers=headers, data=payload)
    # for ticket_forms in response.json()["ticket_forms"]:
    #     print(ticket_forms["id"], ticket_forms["name"])


    # ticket = zenpy_client.tickets(id=ticketid)
    # print(ticket)


    # fields = []
    # url = "https://grupocard.zendesk.com/api/v2/ticket_fields"
    # payload = {}
    # headers = {
    #     'Authorization': ZENDESK_BASICAUTH,
    # }
    # response = requests.request("GET", url, headers=headers, data=payload)
    # for ticket_fields in response.json()["ticket_fields"]:
    #     if "status" in ticket_fields["type"]:
    #         continue
    #     if "group" in ticket_fields["type"]:
    #         continue
    #     if "assignee" in ticket_fields["type"]:
    #         continue
    #     if "subject" in ticket_fields["type"]:
    #         continue
    #     if "description" in ticket_fields["type"]:
    #         continue
    #     if "tickettype" in ticket_fields["type"]:
    #         continue
    #     if "priority" in ticket_fields["type"]:
    #         continue
    #     fields.append(ticket_fields["id"])
    # print("fields ", fields, len(fields))


    print("asdasdsdsd--------------------------")
    fields_conditions = []
    for ticket_field_ids in tickets_ticket_field_ids:
        for agent_conditions in tickets_agent_conditions:
            if not ticket_field_ids == agent_conditions["parent_field_id"]:
                continue
            print(agent_conditions["parent_field_id"], agent_conditions["value"])

            if not agent_conditions['parent_field_id'] in fields_conditions:
                fields_conditions.append(agent_conditions['parent_field_id'])
            for child_fields in agent_conditions['child_fields']:
                if child_fields['id'] in fields_conditions:
                    continue
                # if "ALL_STATUSES" in child_fields['required_on_statuses']['type']:
                #     continue
                # if "SOME_STATUSES" in child_fields['required_on_statuses']['type']:
                #     continue
                fields_conditions.append(child_fields['id'])
    print("campos: ", fields_conditions, len(fields_conditions))


if __name__ == '__main__':
    main()
    sys.exit(0)