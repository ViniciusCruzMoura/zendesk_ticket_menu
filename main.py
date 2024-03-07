import sys
from decouple import config
import requests
from zenpy import Zenpy

#zendesk
ZENDESK_EMAIL = config('ZENDESK_EMAIL', '')
ZENDESK_PASSWORD = config('ZENDESK_PASSWORD', '')
ZENDESK_DOMAIN = config('ZENDESK_DOMAIN', '')
ZENDESK_BASICAUTH = config('ZENDESK_BASICAUTH', '')
ZENDESK_URL = config('ZENDESK_URL', '')

#oracle
USR= config('USR', '')
PASSWD = config('PASSWD', '')
HOST = config('HOST', '')

#receita, sefaz
RECEITAWS = config('RECEITAWS', '')
SEFAZWS = config('RECEITAWS', '')

def get_zenpy_connection():
    creds = {
        'email': ZENDESK_EMAIL,
        'token': ZENDESK_PASSWORD,
        'subdomain': ZENDESK_DOMAIN,
    }
    session = requests.Session()
    zenpy_client = Zenpy(**creds, session=session)

    return zenpy_client

def ORACLE_exec_sql(sql, type=""):
    words = ["DROP", "DELETE", "ALTER"]
    for word in words:
        if word in sql:
            raise Exception("dangerous sql detected")
    
    if "SELECT" in sql:
        type="qry"

    import cx_Oracle
    result = ''
    conn = cx_Oracle.connect(
        user=f'{USR}',
        password=f'{PASSWD}',
        dsn=f'{HOST}',
    )
    try:
        cur = conn.cursor()
        cur.execute(sql)
        if type == 'qry':
            result = [
                dict(zip([col[0] for col in cur.description], row))
                for row in cur.fetchall()
            ]
    except cx_Oracle.DatabaseError as err:
        import traceback
        print(err)
        traceback.print_exc()
        result = err
    finally:
        if conn is not None:
            conn.close()
    return result

def roda_sql_oracle_utls(vsql, tipo):
    import cx_Oracle
    resultado = ''
    conn = cx_Oracle.connect(
        user=f'{USR}',
        password=f'{PASSWD}',
        dsn=f'{HOST}',
    )
    try:
        # Executando a consulta
        cur = conn.cursor()
        cur.execute(vsql)
        if tipo == 'qry':
            resultado = cur.fetchall()
    except cx_Oracle.DatabaseError as error:
        print(error)
        resultado = error
    finally:
        if conn is not None:
            conn.close()
    return resultado

def ext_sigla():
    import time, re, requests, json
    start = time.time()
    sql = f""" SELECT * FROM ADM_SGV_CAD.EMPRESA e """
    emp_list = roda_sql_oracle_utls(sql, "qry")
    dados_ext = []
    for emp in emp_list:
        id = emp[0]
        cnpj = re.compile(r"[^0-9]").sub("", emp[1])
        razao = emp[2]
        fantasia = emp[3]
        sigla = ""

        url = f"{RECEITAWS}"
        payload = json.dumps(
            {
                "cnpj": cnpj
            }
        )
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        try:
            sigla = requests.request("POST", url, data=payload, headers=headers).json()["uf"]
        except Exception as err:
            print("Exception: ", err, " continue data extraction...")

        dados = {
            "id": id,
            "cnpj": cnpj,
            "razao": razao,
            "fantasia": fantasia,
            "sigla": sigla,
        }
        print(dados)
        dados_ext.append(dados)
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(dados_ext, f, ensure_ascii=False, indent=4)
    end = time.time()
    print("Processamento demorou: ", end - start)

def main():
    ticketid = 1134721#2425717#2420520#1134721
    zenpy_client = get_zenpy_connection()

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
            
            
            # url = f"{ZENDESK_URL}/api/v2/ticket_fields/{agent_conditions['parent_field_id']}/options"
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
    # url = f"{ZENDESK_URL}/api/v2/ticket_fields"
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


    print("--------------------------")
    print("--------------------------")
    fields_conditions = []
    for ticket_field_ids in tickets_ticket_field_ids:
        for agent_conditions in tickets_agent_conditions:
            if not ticket_field_ids == agent_conditions["parent_field_id"]:
                continue
            
            print(agent_conditions["parent_field_id"], agent_conditions["value"])

            
            deve_add = False
            for child_fields in agent_conditions['child_fields']:
                # print(child_fields)
                if child_fields['id'] in fields_conditions:
                    continue
                if not child_fields['id'] == ticket_field_ids:
                    continue 
                # if not child_fields['is_required']:
                #     continue 
                if "ALL_STATUSES" in child_fields['required_on_statuses']['type']:
                    deve_add = True
                # if "SOME_STATUSES" in child_fields['required_on_statuses']['type']:
                #     continue
                # if "NO_STATUSES" in child_fields['required_on_statuses']['type']:
                #     continue
                # fields_conditions.append(child_fields['id'])
            if deve_add:
                if not agent_conditions['parent_field_id'] in fields_conditions:
                    fields_conditions.append(agent_conditions['parent_field_id'])
            
            
    print("campos: ", fields_conditions, len(fields_conditions))
    for fields in fields_conditions:
        url = f"{ZENDESK_URL}/api/v2/ticket_fields/{fields}"
        payload = {}
        headers = {
            'Authorization': ZENDESK_BASICAUTH,
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if not response.json()["ticket_field"]["required"]:
            print(fields, response.json()["ticket_field"]["title"])
			
	# 'lista_de_status': [
    #     {
    #         #"item": 1500010139582,
    #         "item": 'open',
    #         "label": "Aberto"
    #     },
    #     {
    #         #"item": 1500010139602,
    #         "item": 'pending',
    #         "label": "Pendente"
    #     },
    #     {
    #         #"item": 1500010139622,
    #         "item": 'hold',
    #         "label": "Em espera"
    #     },
    #     {
    #         #"item": 1500010139642,
    #         "item": 'solved',
    #         "label": "Resolvido"
    #     },
    # ],

def main2():
    import json, time
    estados_dict = [
        "AC",
        "AL",
        "AM",
        "AP",
        "BA",
        "CE",
        "DF",
        "ES",
        "GO",
        "MA",
        "MG",
        "MS",
        "MT",
        "PA",
        "PB",
        "PE",
        "PI",
        "PR",
        "RJ",
        "RN",
        "RO",
        "RR",
        "RS",
        "SC",
        "SE",
        "SP",
        "TO",
    ]
    start = time.time()
    for estado in estados_dict:
        url = f"{SEFAZWS}"
        payload = json.dumps(
            {
                "cnpj": "45272357000167",
                "uf": estado.lower()
            }
        )
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        # print(response.text)
        if response.status_code > 299:
            continue
        try:
            motivo = response.json()["soap:Envelope"]["soap:Body"]["nfeResultMsg"]["retConsCad"]["infCons"]["xMotivo"]
        except Exception as err:
            # print("deu pau    ", payload)
            continue
        if "Rejeicao" in motivo:
            continue
        else:
            print(payload)
            print("---------------------")
            print(response.text)
            break
    end = time.time()
    print("Processamento demorou: ", end - start)

if __name__ == '__main__':
    # main2()
    sys.exit(0)