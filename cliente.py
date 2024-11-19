import tkinter as tk
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

# Função para receber mensagens do servidor
def receber_mensagens():
    while True:
        try:
            mensagem = cliente_socket.recv(1500)
            if mensagem:
                log_text.insert(tk.END, f"Servidor: {mensagem.decode()}\n")
            else:
                break
        except:
            break

# Função para conectar ao servidor
def conectar_servidor():
    try:
        cliente_socket.connect(('127.0.0.1', int(porta_entrada.get())))
        log_text.insert(tk.END, f"Conectado ao servidor na porta {porta_entrada.get()}...\n")

        # Thread para receber mensagens continuamente
        Thread(target=receber_mensagens).start()
    except Exception as e:
        log_text.insert(tk.END, f"Erro ao conectar ao servidor: {e}\n")

# Função para enviar mensagens ao servidor
def enviar_mensagem():
    mensagem = entrada_mensagem.get()
    entrada_mensagem.delete(0, tk.END)
    cliente_socket.send(mensagem.encode())
    log_text.insert(tk.END, f"Você: {mensagem}\n")

# Configuração da interface gráfica
janela = tk.Tk()
janela.title("Cliente")

log_text = tk.Text(janela, height=15, width=50)
log_text.pack()

porta_entrada = tk.Entry(janela, width=10)
porta_entrada.insert(0, "8000")  # Porta padrão
porta_entrada.pack()

entrada_mensagem = tk.Entry(janela, width=40)
entrada_mensagem.pack()

botao_enviar = tk.Button(janela, text="Enviar", command=enviar_mensagem)
botao_enviar.pack()

# Botão para conectar ao servidor
botao_conectar = tk.Button(janela, text="Conectar", command=conectar_servidor)
botao_conectar.pack()

# Inicializa o socket do cliente
cliente_socket = socket(AF_INET, SOCK_STREAM)

# Loop principal da interface
janela.mainloop()

# Fecha a conexão ao sair
cliente_socket.close()
