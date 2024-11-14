import tkinter as tk
from tkinter import Toplevel, filedialog, messagebox, ttk, Label, Button, Entry, PhotoImage
import requests
from io import BytesIO
from PIL import Image, ImageTk
import config  # Módulo separado para armazenar a variável session_value
import base64
import threading
import time
import os
import pandas as pd
import re

# URL base da API
API_INICIAR_SESSAO_BASE = "http://localhost:3000/session/start/"
API_OBTER_IMAGEM_BASE = "http://localhost:3000/session/qr/"
API_STATUS_BASE = "http://localhost:3000/session/status/"
API_URL = "http://localhost:3000/client/sendMessage/"
API_KEY = "solprovedor"

HEADERS = {
    "x-api-key": API_KEY
}

# Variável global para armazenar os dados do arquivo
dados_excel = []

# Função para normalizar os números de telefone
def formatar_numero(numero):
    # Remove caracteres não numéricos
    numero = re.sub(r'\D', '', numero)
    # Verifica se o número começa com 55, senão adiciona
    if not numero.startswith("55"):
        numero = "55" + numero
    # Remove o '9' extra se for um número com 9 dígitos no início após o código do país
    if len(numero) > 4 and numero[4] == '9':
        numero = numero[:4] + numero[5:]
    return numero

# Função para carregar o arquivo de números de telefone e variáveis
def carregar_arquivo():
    filepath = filedialog.askopenfilename(
        title="Selecione um arquivo CSV ou Excel",
        filetypes=[("Arquivos Excel", "*.xlsx"), ("Arquivos CSV", "*.csv")]
    )
    if filepath:
        try:
            global dados_excel
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)

            # Assumindo que a primeira coluna contém números e a segunda coluna contém variáveis
            dados_excel = df.values.tolist()
            numeros = [formatar_numero(str(linha[1])) for linha in dados_excel]

            phone_entry.delete(1, tk.END)
            phone_entry.insert(1, ', '.join(numeros))
            file_label.config(text=f"Arquivo carregado: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar o arquivo: {e}")

# Função para anexar um arquivo
def anexar_arquivo():
    filepath = filedialog.askopenfilename(
        title="Selecione um arquivo para anexar",
        filetypes=[("Todos os arquivos", "*.*")]
    )
    if filepath:
        attach_label.config(text=f"Anexo selecionado: {os.path.basename(filepath)}")
        global selected_attachment
        selected_attachment = filepath

# Função para codificar o arquivo em base64
def codificar_base64(filepath):
    with open(filepath, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
    return encoded_string

# Função para executar a ação e enviar a solicitação POST
def executar_acao():
    mensagem = message_entry.get("1.0", tk.END).strip()
    tempo = time_entry.get()
    numeros_input = phone_entry.get()

    if not mensagem:
        messagebox.showwarning("Aviso", "Preencha o campo de mensagem antes de executar.")
        return

    # if 'selected_attachment' not in globals():
    #     messagebox.showwarning("Aviso", "Nenhum anexo foi selecionado.")
    #     return

    # Dividir os números por vírgula e remover espaços
    numeros_lista = [formatar_numero(num.strip()) for num in numeros_input.split(',') if num.strip()]

    if not numeros_lista and not dados_excel:
        messagebox.showwarning("Aviso", "Insira pelo menos um número de telefone ou carregue um arquivo.")
        return

    # Usar os números do arquivo se carregado
    if dados_excel:
        numeros_lista = [formatar_numero(str(linha[1])) for linha in dados_excel]

    try:
        delay = int(tempo) if tempo else 0  # Tempo opcional, padrão 0
    except ValueError:
        messagebox.showerror("Erro", "O campo de tempo deve ser um número inteiro.")
        return
    if 'selected_attachment' in globals():
        anexo_base64 = codificar_base64(selected_attachment)
        filename = os.path.basename(selected_attachment)

    for numero in numeros_lista:
        variavel = ""
        for linha in dados_excel:
            if formatar_numero(str(linha[1])) == numero:
                variavel = str(linha[0]) if len(linha) > 1 else ""
                break

        mensagem_personalizada = mensagem.replace("{var}", variavel)

        # JSON de envio
        if 'selected_attachment' not in globals():
            json_data = {
                "chatId": f"{numero}@c.us",
                "contentType": "string",
                "content": mensagem_personalizada
            }
        else:
            json_data = {
                "chatId": f"{numero}@c.us",
                "contentType": "MessageMedia",
                "content": {
                    "mimetype": "image/jpeg",  # Mude conforme o tipo do arquivo
                    "data": anexo_base64,
                    "filename": filename

                },
                "options": {
                    "caption": mensagem_personalizada
                }
            }


        # Cabeçalho da solicitação
        headers = {
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        }

        # Envia a solicitação POST
        response = requests.post(API_URL+config.session_value, json=json_data, headers=headers)
        if response.status_code == 200:
            print(f"Mensagem enviada para {numero} com sucesso!")
        else:
            print(f"Erro ao enviar mensagem para {numero}: {response.status_code} - {response.text}")

    messagebox.showinfo("Sucesso", "Ação executada com sucesso!")

# Funções relacionadas à sessão
def carregar_sessao():
    try:
        with open("session.txt", "r") as file:
            config.session_value = file.read().strip()
            return config.session_value
    except FileNotFoundError:
        return None

def salvar_sessao(session_id):
    with open("session.txt", "w") as file:
        file.write(session_id)

def iniciar_sessao(entry_session, label_status):
    session_id = entry_session.get().strip()
    if not session_id:
        messagebox.showwarning("Aviso", "Informe um ID de sessão!")
        return

    api_iniciar_sessao = API_INICIAR_SESSAO_BASE + session_id

    try:
        response = requests.get(api_iniciar_sessao, headers=HEADERS)
        if response.status_code == 200:
            config.session_value = session_id
            salvar_sessao(session_id)
            label_status.config(text="Sessão iniciada com sucesso!", fg="green")
        else:
            label_status.config(text="Erro ao iniciar sessão", fg="red")
    except Exception as e:
        label_status.config(text=f"Erro: {e}", fg="red")

def verificar_status(label_status, label_icon):
    def atualizar_status():
        while True:
            session_id = config.session_value
            if session_id:
                try:
                    response = requests.get(API_STATUS_BASE + session_id, headers=HEADERS)
                    if response.status_code == 200 and response.json().get("state") == "CONNECTED":
                        label_status.config(text="Conectado", fg="green")
                        label_icon.config(text="🟢")
                    else:
                        label_status.config(text="Desconectado", fg="red")
                        label_icon.config(text="🔴")
                except:
                    label_status.config(text="Erro", fg="red")
                    label_icon.config(text="🔴")
            time.sleep(5)

    threading.Thread(target=atualizar_status, daemon=True).start()

def exibir_qr_code(label_imagem):
    session_id = config.session_value
    if not session_id:
        messagebox.showwarning("Aviso", "Nenhuma sessão carregada.")
        return

    api_obter_imagem = API_OBTER_IMAGEM_BASE + session_id + "/image"

    try:
        response = requests.get(api_obter_imagem, headers=HEADERS)
        if response.status_code == 200:
            image_data = response.content
            image = Image.open(BytesIO(image_data))
            image_tk = ImageTk.PhotoImage(image)
            label_imagem.config(image=image_tk)
            label_imagem.image = image_tk
        else:
            messagebox.showerror("Erro", "Erro ao obter imagem.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro: {e}")

# Layout da interface principal
root = tk.Tk()
root.title("Interface Principal")
root.geometry("500x800")
root.configure(bg="white")

# Função para aplicar estilos arredondados
style = ttk.Style()
style.configure("TEntry", padding=5)
style.configure("TButton", padding=5, relief="flat", borderwidth=0)

# Logo
logo = tk.PhotoImage(file="imagens/logo.png")  # Substitua "logo.png" pelo caminho correto da sua imagem
logo_label = tk.Label(root, image=logo, bg="white")
logo_label.pack(pady=20)

label_phone = tk.Label(root, text="Número de Telefone:", bg="white", font=("Arial", 12), fg="#333")
label_phone.pack(anchor="w", padx=30)
phone_entry = ttk.Entry(root, font=("Arial", 12))
phone_entry.pack(fill="x", padx=30, pady=5)

load_button = tk.Button(root, text="Carregar Arquivo", command=carregar_arquivo, bg="#00b7c2", fg="white", font=("Arial", 12, "bold"))
load_button.pack(anchor="w", padx=30, pady=5)
file_label = tk.Label(root, text="Nenhum arquivo carregado", bg="white", fg="gray", font=("Arial", 10))
file_label.pack(anchor="w", padx=30)

label_message = tk.Label(root, text="Mensagem:", bg="white", font=("Arial", 12), fg="#333")
label_message.pack(anchor="w", padx=30)
message_entry = tk.Text(root, height=5, font=("Arial", 12))
message_entry.pack(fill="x", padx=30, pady=5)

label_time = tk.Label(root, text="Tempo (em segundos):", bg="white", font=("Arial", 12), fg="#333")
label_time.pack(anchor="w", padx=30)
time_entry = ttk.Entry(root, font=("Arial", 12))
time_entry.pack(fill="x", padx=30, pady=5)

attach_button = tk.Button(root, text="Anexar Arquivo (Opcional)", command=anexar_arquivo, bg="#00b7c2", fg="white", font=("Arial", 12, "bold"))
attach_button.pack(anchor="w", padx=30, pady=5)
attach_label = tk.Label(root, text="Nenhum anexo selecionado", bg="white", fg="gray", font=("Arial", 10))
attach_label.pack(anchor="w", padx=30)

run_button = tk.Button(root, text="Executar", command=executar_acao, bg="#00b7c2", fg="white", font=("Arial", 12, "bold"))
run_button.pack(pady=20, padx=30, fill="x")

def abrir_popup():
    popup = Toplevel(root)
    popup.title("Interface com Sess")
    # Configurações da interface do pop-up
    popup.geometry("600x600")
    popup.configure(bg="white")

    session_label = tk.Label(popup, text="ID da Sessão:", bg="white", font=("Arial", 12), fg="#333")
    session_label.pack(anchor="w", padx=20, pady=5)

    session_entry = tk.Entry(popup, font=("Arial", 12))
    session_entry.pack(fill="x", padx=20, pady=5)

    iniciar_button = tk.Button(
        popup, text="Iniciar Sessão", command=lambda: iniciar_sessao(session_entry, session_status_label),
        bg="#00b7c2", fg="white", font=("Arial", 12, "bold")
    )
    iniciar_button.pack(pady=10, padx=20, fill="x")

    session_status_label = tk.Label(popup, text="Status da Sessão", bg="white", font=("Arial", 12), fg="gray")
    session_status_label.pack(anchor="w", padx=20)

    session_icon_label = tk.Label(popup, text="🔴", bg="white", font=("Arial", 20))
    session_icon_label.pack(pady=5)

    verificar_status(session_status_label, session_icon_label)

    qr_code_button = tk.Button(
        popup, text="Exibir QR Code", command=lambda: exibir_qr_code(qr_image_label),
        bg="#00b7c2", fg="white", font=("Arial", 12, "bold")
    )
    qr_code_button.pack(pady=10, padx=20, fill="x")

    qr_image_label = tk.Label(popup, bg="white")
    qr_image_label.pack(pady=5)

# Botão para abrir o pop-up
popup_button = tk.Button(root, text="Configurações de Sessão", command=abrir_popup, bg="#00b7c2", fg="white", font=("Arial", 12, "bold"))
popup_button.pack(pady=10, padx=30, fill="x")

# Verificar se a sessão foi carregada ao iniciar a interface
carregar_sessao()

root.mainloop()
