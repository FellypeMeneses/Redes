import socket
import sys
import struct
import random
import os

def obter_servidor_dns_local():
    """Obtém o endereço do servidor DNS local do sistema."""
    try:
        if os.name == 'nt':  # Windows
            import subprocess
            resultado = subprocess.run(['nslookup'], capture_output=True, text=True)
            for linha in resultado.stdout.splitlines():
                if 'Default Server' in linha or 'Servidor padrão' in linha:
                    return linha.split(':')[-1].strip()
        else:  # Linux/Mac
            with open('/etc/resolv.conf', 'r') as f:
                for linha in f:
                    if linha.startswith('nameserver'):
                        return linha.split()[1]
    except Exception as e:
        print(f"Erro ao obter o servidor DNS local: {e}")
    return '8.8.8.8'  # Retorna o servidor DNS do Google como fallback

def criar_cabecalho():
    """Cria o cabeçalho do pacote DNS."""
    identificacao = random.randint(0, 65535)
    flags = 0x0100  # Consulta padrão
    qdcount = 1  # Número de perguntas (queries)
    ancount = 0  # Número de respostas (answers)
    nscount = 0  # Número de autoridades (authorities)
    arcount = 0  # Número de registros adicionais (additional records)

    return struct.pack('>HHHHHH', identificacao, flags, qdcount, ancount, nscount, arcount), identificacao

def criar_query(nome_dominio, tipo_registro):
    """Cria a query DNS para o domínio e tipo especificado."""
    partes = nome_dominio.split('.')
    query = b''
    for parte in partes:
        query += struct.pack('B', len(parte)) + parte.encode('utf-8')
    query += b'\x00'

    tipos = {'A': 1, 'AAAA': 28, 'MX': 15}
    tipo = tipos.get(tipo_registro.upper(), 1)
    classe = 1  # Classe IN (Internet)

    return query + struct.pack('>HH', tipo, classe)

def enviar_consulta(dns_server, pacote):
    """Envia a consulta DNS para o servidor especificado."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(5)
        s.sendto(pacote, (dns_server, 53))
        resposta, _ = s.recvfrom(512)
    return resposta

def parse_resposta(resposta, identificacao):
    """Analisa a resposta DNS."""
    cabecalho = resposta[:12]
    resposta_id, flags, qdcount, ancount, nscount, arcount = struct.unpack('>HHHHHH', cabecalho)

    if resposta_id != identificacao:
        raise ValueError("ID de resposta não corresponde à ID da consulta.")

    if ancount == 0:
        print("Nenhuma resposta encontrada.")
        return

    resposta_offset = 12
    for _ in range(qdcount):
        while resposta[resposta_offset] != 0:
            resposta_offset += 1 + resposta[resposta_offset]
        resposta_offset += 5  # Ignora o \x00 final e QTYPE/QCLASS

    print("Respostas:")
    for _ in range(ancount):
        while resposta[resposta_offset] != 0:
            resposta_offset += 1 + resposta[resposta_offset]
        resposta_offset += 1  # Ignora o \x00 final

        tipo, classe, ttl, rdlength = struct.unpack('>HHIH', resposta[resposta_offset:resposta_offset + 10])
        resposta_offset += 10

        if tipo == 1:  # Registro A
            ip = struct.unpack('>BBBB', resposta[resposta_offset:resposta_offset + 4])
            print(f"- Endereço IPv4: {'.'.join(map(str, ip))}")
        elif tipo == 28:  # Registro AAAA
            ipv6 = resposta[resposta_offset:resposta_offset + 16]
            print(f"- Endereço IPv6: {':'.join(f'{ipv6[i]:02x}{ipv6[i+1]:02x}' for i in range(0, 16, 2))}")
        elif tipo == 15:  # Registro MX
            preference = struct.unpack('>H', resposta[resposta_offset:resposta_offset + 2])[0]
            mx_nome = resposta[resposta_offset + 2:resposta_offset + rdlength]
            print(f"- Servidor de e-mail: {mx_nome.decode('utf-8')} (preferência: {preference})")
        else:
            print(f"- Tipo {tipo} não suportado.")

        resposta_offset += rdlength

def main():
    if len(sys.argv) < 2:
        print("Uso: cliente_dns <dominio> [<tipo_registro>] [@<servidor_dns>]")
        sys.exit(1)

    nome_dominio = sys.argv[1]
    tipo_registro = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('@') else 'A'
    servidor_dns = sys.argv[3][1:] if len(sys.argv) > 3 and sys.argv[3].startswith('@') else obter_servidor_dns_local()

    cabecalho, identificacao = criar_cabecalho()
    query = criar_query(nome_dominio, tipo_registro)
    pacote = cabecalho + query

    try:
        resposta = enviar_consulta(servidor_dns, pacote)
        parse_resposta(resposta, identificacao)
    except Exception as e:
        print(f"Erro ao realizar consulta DNS: {e}")

if __name__ == '__main__':
    main()