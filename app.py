from flask import Flask, request, jsonify
from services.waha import Waha
from random import randint
from time import sleep
import threading
from datetime import datetime
import socket


app = Flask(__name__)
status_table_option = True
dict_chat: dict = {}

SERVER_IP = "192.168.0.103"
PORT = 80

def time_message():
    global dict_chat

    while True:
        sleep(120)
        print('dict: ', dict_chat)
        print('Se passou 2 min!')
        now_date        =  datetime.now()
        now_hour        =  now_date.hour
        now_minute      =  now_date.minute

        if len(dict_chat) > 0:
            for chat_id in dict_chat.keys():
                data_message    =  dict_chat[f'{chat_id}']['last_message']
                hour_user       =  data_message.hour
                minute_user     =  data_message.minute

                transforme_secund_user = ((hour_user * 60) + minute_user) * 60
                transforme_secund_system = ((now_hour * 60) + now_minute) * 60

                if (transforme_secund_system - transforme_secund_user) >= 120:
                    del dict_chat[f'{chat_id}']

def run_time_message():
    threading.Thread(target=time_message, daemon=True).start()

def send_command(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, PORT))
        s.sendall(command.encode())
        print(f"Comando enviado: {command}")

@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    global dict_chat, status_table_option

    print(dict_chat)
    data = request.json

    waha = Waha()

    run_time_message()

    chat_id = data['payload']['from']
    waha.start_typing(chat_id)
    lead_time = randint(1, 5)
    sleep(lead_time)

    
    notify_name = data['payload']['_data']['notifyName']

    if chat_id in dict_chat.keys():
        body = data['payload']['_data']['body']

        if not status_table_option:
            match body:
                case '1':
                    send_command("Alert 1")
                    send_command("BUZZER_ON")
                    message = (
                        "O alerta foi ativado com sucesso!"
                    )

                case '2':
                    send_command("MATRIZ_LED_ANIMATION_ON")
                    message = (
                        "O animação foi ativado com sucesso!"
                    )

                case '3':
                    send_command("LED_ON")
                    sleep(3)
                    send_command("LED_OFF")

                    message = (
                        "O led foi ativado com sucesso!"
                    )
                
                case _:
                    message = "Opção inválida. Por favor, escolha uma das opções disponíveis."

            message += (
                f"\n\nOlá {notify_name}, por favor escolha uma das opções abaixo:\n\n"
                "1 - Alerta para Tomar Remédios\n"
                "2 - Ativa animação\n"
                "3 - Ligar Led\n")
                
        #else:
        #    message = (
        #        f"Olá {notify_name}, por favor escolha uma das opções abaixo:\n\n"
        #        "1 - Alerta para Tomar Remédios\n"
        #        "2 - Ativa animação\n"
        #        "3 - Ligar Led\n"
        #    )
        #    status_table_option = True

    else:
        dict_chat[f'{chat_id}'] = {'last_message': datetime.now()}
        message = (
                f"Olá {notify_name}, por favor escolha uma das opções abaixo:\n\n"
                "1 - Alerta para Tomar Remédios\n"
                "2 - Ativa animação\n"
                "3 - Ligar Led\n"
            )
        status_table_option = False
        

    waha.send_message(chat_id=chat_id, message=message)
    waha.stop_typing(chat_id)

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)