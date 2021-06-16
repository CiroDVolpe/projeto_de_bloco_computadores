import socket, pickle
import psutil
import shutil
import platform
import cpuinfo
import os
import sched
import time
import subprocess
from nmap import PortScanner
from datetime import datetime

HOST = socket.gethostname()
PORT = 8888
ORIG = (HOST, PORT)
CPU_INFO = cpuinfo.get_cpu_info()
NUM_OF_CPUS = len(psutil.cpu_percent(interval=1, percpu=True))
DIR = './files'
FILES = os.listdir(DIR)
NM = PortScanner()
start_time = call_time = exec_time = start_clock = exec_clock = 0

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind(ORIG)

def encoded_resp(resp, client):
  byte_resp = pickle.dumps(str(resp))
  client.send(byte_resp)

def initial_spec():
  initial_info = {
    "summary": {
      "ip": socket.gethostbyname(socket.gethostname())
    }
  }
  return initial_info

def memory_spec():
  return psutil.virtual_memory().percent

def disk_spec():
  return (shutil.disk_usage('/').used / shutil.disk_usage('/').total)*100

def summary_spec():
  summary_info = {
    "cpu": psutil.cpu_percent(interval=0),
    "memory": memory_spec(),
    "disk": disk_spec()
  }
  return summary_info

tcp.listen()
print('Servidor pronto!')
(cliente,addr) = tcp.accept()
while True:
  encoded_msg = cliente.recv(1024)
  msg = encoded_msg.decode('ascii')
  print("Pedido", msg)

  if msg == "exit":
    break
  if msg == "initial":
    encoded_resp(initial_spec(), cliente)
  # if msg == "net":
  #   encoded_resp(net_spec(), cliente)
  # if msg == "ip": # split with space
  #   encoded_resp(ip_spec(args), cliente)
  if msg == "summary":
    encoded_resp(summary_spec(), cliente)
  # if msg == "cpu":
  #   encoded_resp(cpu_spec(), cliente)
  if msg == "memory":
    encoded_resp(memory_spec(), cliente)
  if msg == "disk":
    encoded_resp(disk_spec(), cliente)
  # if msg == "files":
  #   encoded_resp(files_spec(), cliente)
  # if msg == "process":
  #   encoded_resp(process_spec(), cliente)
  else:
    pass
    # encoded_resp("Erro: requisicao invalida", cliente)

tcp.close()
