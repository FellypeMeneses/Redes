import tkinter as tk
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

# Função para receber mensagens do servidor
def receber_mensagens():
    while True:
        try:
            mensagem = cliente_socket.recv(1500)
            if mensagem:
                if mensagem.decode().startswith("UPDATE_LIST:"):
                    atualizar_lista_clientes(mensagem.decode().split(":", 1)[1])
                else:
                    log_text.insert(tk.END, f"{mensagem.decode()}\n")
            else:
                break
        except:
            break

# Função para conectar ao servidor
def conectar_servidor():
    global cliente_nome
    cliente_nome = nome_entrada.get().strip()  # Obtém o nome do cliente
    if not cliente_nome:
        log_text.insert(tk.END, "Por favor, insira um nome antes de conectar.\n")
        return
    try:
        cliente_socket.connect(('127.0.0.1', int(porta_entrada.get())))
        cliente_socket.send(cliente_nome.encode())  # Envia o nome ao servidor
        log_text.insert(tk.END, f"Conectado ao servidor como {cliente_nome}...\n")

        # Thread para receber mensagens continuamente
        Thread(target=receber_mensagens).start()
    except Exception as e:
        log_text.insert(tk.END, f"Erro ao conectar ao servidor: {e}\n")

# Função para atualizar a lista de clientes conectados
def atualizar_lista_clientes(clientes):
    clientes_lista.delete(0, tk.END)
    for cliente in clientes.split(','):
        if cliente != cliente_nome:  # Remove o próprio nome da lista
            clientes_lista.insert(tk.END, cliente)

# Função para enviar mensagem para o cliente selecionado
def enviar_para_cliente():
    mensagem = entrada_mensagem.get()

    # Verifica se algum cliente foi selecionado
    if not clientes_lista.curselection():
        log_text.insert(tk.END, "Selecione um cliente para enviar a mensagem.\n")
        return

    cliente_selecionado = clientes_lista.get(clientes_lista.curselection())  # Pega o cliente selecionado

    cliente_socket.send(f"{cliente_selecionado}:{mensagem}".encode())  # Envia para o servidor com o nome do destinatário
    log_text.insert(tk.END, f"Você para {cliente_selecionado}: {mensagem}\n")
    entrada_mensagem.delete(0, tk.END)

# Configuração da interface gráfica
janela = tk.Tk()
janela.title("Cliente")

log_text = tk.Text(janela, height=15, width=50)
log_text.pack()

tk.Label(janela, text="Nome:").pack()
nome_entrada = tk.Entry(janela, width=20)
nome_entrada.insert(0, "MeuNome")  # Nome padrão
nome_entrada.pack()

tk.Label(janela, text="Porta:").pack()
porta_entrada = tk.Entry(janela, width=10)
porta_entrada.insert(0, "8000")  # Porta padrão
porta_entrada.pack()

entrada_mensagem = tk.Entry(janela, width=40)
entrada_mensagem.pack()

# Botão para enviar mensagem
botao_enviar = tk.Button(janela, text="Enviar", command=enviar_para_cliente)
botao_enviar.pack()

# Botão para conectar ao servidor
botao_conectar = tk.Button(janela, text="Conectar", command=conectar_servidor)
botao_conectar.pack()

# Lista de clientes conectados
clientes_lista = tk.Listbox(janela, height=6, width=40)
clientes_lista.pack()

# Inicializa o socket do cliente
cliente_socket = socket(AF_INET, SOCK_STREAM)

# Variável global para armazenar o nome do cliente
cliente_nome = ""

# Loop principal da interface
janela.mainloop()

# Fecha a conexão ao sair
cliente_socket.close()
