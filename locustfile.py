import pandas as pd
from locust import HttpUser, task, between
from bs4 import BeautifulSoup
import csv

class FormUser(HttpUser):
    wait_time = between(5, 10)  # Simular pausas entre tareas

    @task
    def submit_form(self):
        # Leer los datos desde un archivo CSV
        datos = pd.read_csv("datos.csv")
        
        # Archivo para guardar respuestas
        with open("respuestas_formularios.csv", "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Nombre", "Apellido", "Email", "Estado Primer Formulario", "Estado Segundo Formulario"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Enviar el formulario para cada registro
            for _, row in datos.iterrows():
                nombre = row["Nombre"]
                apellido = row["Apellido"]
                email = row["Email"]

                # Datos del primer formulario
                first_form_data = {
                    "firstname": nombre,
                    "lastname": apellido,
                    "email": email,
                    "afft_": "",
                    "aff_": "",
                    "sess_": "",
                    "ref_": "",
                    "own_": "",
                    "oprid": "",
                    "contact_id": "",
                    "utm_source": "",
                    "utm_medium": "",
                    "utm_term": "",
                    "utm_content": "",
                    "utm_campaign": "",
                    "referral_page": "",
                    "_op_gclid": "",
                    "_op_gcid": "",
                    "_fbc": "",
                    "_fbp": "",
                    "uid": "p2c28043f384",
                    "uniquep2c28043f384": "1",
                    "mopsbbk": "961270BC12AB33A377DFCCF1:0C04778CE350B643F2F82CEE",
                    "mopbelg": "0175599:1C17C9D09F2B887171F8E415:CD6658F11BFD1F1EAC613BE1",
                }

                # Enviar el primer formulario
                response = self.client.post("/v2.4/form_processor.php", data=first_form_data)
                estado_primero = response.status_code

                # Redirigir al segundo formulario si el primero es exitoso
                if estado_primero == 200:
                    second_form_url = "https://grupo-bienahora.mytemporarydomain.com/"
                    response = self.client.get(second_form_url)
                    cookies = response.cookies
                    soup = BeautifulSoup(response.text, 'html.parser')
                    mopsbbk = soup.find("input", {"name": "mopsbbk"})
                    mopbelg = soup.find("input", {"name": "mopbelg"})

                    # Datos del segundo formulario
                    second_form_data = {
                        "email": email,
                        "f1605": "6660",  # Selección "La Otilia"
                        "uid": "p2c28043f385",
                        "uniquep2c28043f385": "1",
                    }
                    if mopsbbk:
                        second_form_data["mopsbbk"] = mopsbbk["value"]
                    if mopbelg:
                        second_form_data["mopbelg"] = mopbelg["value"]

                    # Enviar el segundo formulario
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
                        "Referer": second_form_url
                    }
                    response = self.client.post("/v2.4/form_processor.php", data=second_form_data, headers=headers, cookies=cookies)
                    estado_segundo = response.status_code

                    # Escribir resultados en el CSV
                    writer.writerow({
                        "Nombre": nombre,
                        "Apellido": apellido,
                        "Email": email,
                        "Estado Primer Formulario": estado_primero,
                        "Estado Segundo Formulario": estado_segundo
                    })
                else:
                    # Si el primer formulario falla, escribir el estado
                    writer.writerow({
                        "Nombre": nombre,
                        "Apellido": apellido,
                        "Email": email,
                        "Estado Primer Formulario": estado_primero,
                        "Estado Segundo Formulario": "No enviado"
                    })

        # Detener la prueba al finalizar todos los registros
        self.environment.runner.quit()
