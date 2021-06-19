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

DIR = './files'
NUM_OF_PROCESS = 5
MAX_HOST_NUM = 10
MY_PID = os.getpid()

######################################################################################################

# BASE
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind(ORIG)

def format_date(date):
  return datetime.fromtimestamp(date).strftime("%d/%m/%Y às %T")

def format_file_path(file):
  return(DIR + '/' + file)

def encoded_resp(resp, client):
  byte_resp = pickle.dumps(str(resp))
  client.send(byte_resp)

######################################################################################################

# PROCESS
def cpu_percent(pid):
  test_list = []
  for i in range(5):
    p = psutil.Process(pid)
    p_cpu = p.cpu_percent(interval=0.1)
    test_list.append(p_cpu)
  return round(float(sum(test_list))/len(test_list), 2)

def processes_info_getter():
  processes = get_process_list()

  processes_info = []
  for p in processes:
    processes_info.append(fill_process_info(p))
  
  return processes_info

def get_process_list():
  listOfProcObjects = []

  for proc in psutil.process_iter():
    try:
      pinfo = proc.as_dict(attrs=['pid', 'name', 'username', 'cpu_percent'])
      pinfo['memory_usage'] = round(proc.memory_info().vms / (1024 * 1024), 2)

      listOfProcObjects.append(pinfo)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
      pass

  listOfProcObjects = sorted(listOfProcObjects, key=lambda process: process['cpu_percent'], reverse=True)

  return listOfProcObjects[:NUM_OF_PROCESS]

def fill_process_info(process):
  process_info = {
    "pid": process['pid'],
    "name": process['name'],
    "cpu_percent": process['cpu_percent'],
    "memory_usage": process['memory_usage'],
    "username": process['username']
  }
  return process_info

######################################################################################################

# NET
def obtem_nome_familia(familia):
  if familia == socket.AF_INET:
    return("IPv4")
  elif familia == socket.AF_INET6:
    return("IPv6")
  elif familia == socket.AF_UNIX:
    return("Unix")
  else:
    return("-")

def obtem_tipo_socket(tipo):
  if tipo == socket.SOCK_STREAM:
    return("TCP")
  elif tipo == socket.SOCK_DGRAM:
    return("UDP")
  elif tipo == socket.SOCK_RAW:
    return("IP")
  else:
    return("-")

def interfaces():
  interfaces = psutil.net_if_addrs()
  interfaces_text = ""

  for i in interfaces:
    nome = str(i)
    interfaces_text = interfaces_text + f"{nome}: \n"
    for info in interfaces[nome]:
      interfaces_text = interfaces_text + f"\t Endereço: {info.address} | Mascara de rede: {info.netmask} | Familia: {obtem_nome_familia(info.family)} \n"
  return interfaces_text

def usage_per_interface():
  io_status = psutil.net_io_counters(pernic=True)
  ios_text = ""
  for i in io_status:
    ios_text = ios_text + f"{str(i)} \n"
    info = io_status[str(i)]
    ios_text = ios_text + f"\t BYTES: Enviados: {info.bytes_sent} | Recebidos: {info.bytes_recv} \n\t PACOTES: Enviados: {info.packets_sent} | Recebidos: {info.packets_recv} \n"
  return ios_text

def usage_per_process():
  n = 0
  pids_text = ""
  pids = psutil.pids()
  for pid in pids:
    try:
      p = psutil.Process(pid)
      conns = p.connections()
      if (conns):
        if n >= NUM_OF_PROCESS:
          break
        n += 1
        for conn in conns:
          familia = obtem_nome_familia(conn.family)
          tipo = obtem_tipo_socket(conn.type)
          status = conn.status
          ip_porta_local = "<" + conn.laddr[0] + ":" + str(conn.laddr[1]) + ">"
          if (conn.raddr):
            ip_porta_remote = "<" + conn.raddr[0] + ":" + str(conn.raddr[1]) + ">"
          else:
            ip_porta_remote = "<>"
          pids_text = pids_text + f"PID: {pid}\n \tFamilia: {familia} | Tipo: {tipo} | status: {status} | IP local: {ip_porta_local} | IP remote: {ip_porta_remote}\n\n"
    except:
      pass
  return pids_text

######################################################################################################

# INITIAL
def initial_spec():
  CPU_INFO = cpuinfo.get_cpu_info()

  FILES = os.listdir(DIR)
  files_specs =[]
  for arq in FILES:
    files_specs.append({
      "name": arq,
      "size": os.path.getsize(format_file_path(arq)),
      "creation_date": format_date(os.stat(format_file_path(arq)).st_ctime),
      "modified_date": format_date(os.stat(format_file_path(arq)).st_mtime),
      "type": arq.split('.')[1]
    })

  interfaces_text = interfaces()
  usage_per_interface_text = usage_per_interface()
  usage_per_process_text = usage_per_process()

  initial_info = {
    "cpu": {
      "num_of_cpus": len(psutil.cpu_percent(interval=1, percpu=True)),
      "name": platform.platform(),
      "arch": CPU_INFO["arch"],
      "bits": CPU_INFO["bits"],
      "freq_min": psutil.cpu_freq().min,
      "freq_max": psutil.cpu_freq().max,
      "freq_cur": psutil.cpu_freq().current,
      "fis_cores": psutil.cpu_count(logical=False),
      "log_cores": psutil.cpu_count()
    },
    "files": {
      "dir": os.getcwd(),
      "num_of_files": len(FILES),
      "files_specs": files_specs
    },
    "process": {
      "pid": MY_PID,
      "perc": cpu_percent(MY_PID),
      "num_of_processes": NUM_OF_PROCESS
    },
    "net": {
      "interfaces": interfaces_text,
      "usage_per_interface": usage_per_interface_text,
      "usage_per_process": usage_per_process_text
    },
    "ip": {
      "my_ip": socket.gethostbyname(socket.gethostname()),
      "max_num_hosts": MAX_HOST_NUM
    },
    "summary": {
      "ip": socket.gethostbyname(socket.gethostname())
    }
  }
  return initial_info

######################################################################################################

# RECURRING SPECS
def cpu_spec():
  return psutil.cpu_percent(interval=0.1, percpu=True)

def memory_spec():
  return psutil.virtual_memory().percent

def disk_spec():
  return (shutil.disk_usage('/').used / shutil.disk_usage('/').total)*100

def process_spec():
  processes_info = {
    "my_cpu_percent": cpu_percent(MY_PID),
    "processes": processes_info_getter()
  }
  return processes_info

def net_spec():
  net_info = {
    "usage_per_interface": usage_per_interface(),
    "usage_per_process": usage_per_process()
  }
  return net_info

def summary_spec():
  summary_info = {
    "cpu": psutil.cpu_percent(interval=0),
    "memory": memory_spec(),
    "disk": disk_spec()
  }
  return summary_info

######################################################################################################

# SCHEDULE
TIME_FORMAT = '%H:%M:%S'
start_time = call_time = exec_time = start_clock = exec_clock = 0

def string_of_now():
  return time.strftime(TIME_FORMAT, time.localtime())

def get_files_by_dir(dir):
  global call_time
  call_time = string_of_now()

  time.sleep(1)
  files = os.listdir(dir)

  global exec_time
  exec_time = string_of_now()

  global exec_clock
  exec_clock = time.process_time()

  return files

def schedule_finder():
  scheduler = sched.scheduler(time.time, time.sleep)

  global start_time
  start_time = string_of_now()

  global start_clock
  start_clock = time.process_time()

  scheduler.enter(1, 3, get_files_by_dir, (DIR,))
  scheduler.run()

def schedule_spec():
  schedule_finder()

  exec_diff_time = (datetime.strptime(exec_time, TIME_FORMAT) - datetime.strptime(call_time, TIME_FORMAT)).seconds
  clock_diff_time = round(exec_clock - start_clock, 7)

  schedule_info = {
    "start_time": start_time,
    "call_time": call_time,
    "exec_time": exec_time,
    "exec_diff_time": exec_diff_time,
    "clock_diff_time": clock_diff_time
  }
  return schedule_info

######################################################################################################

# SUBNET
NM = PortScanner()

def subnet_spec(arg):
  hosts = get_hosts(arg)
  hosts_info = fill_hosts_info(hosts)

  subnet_info = {
    "len": len(hosts),
    "hosts": hosts_info
  }
  return subnet_info

def get_hosts(arg):
  list_ip = arg.split(".")
  net = ".".join(list_ip[0:3]) + "."
  hosts = verify_hosts(net)
  return hosts

def ping_code(hostname):
  if platform.system() == "Windows":
    args = ["ping", "-n", "2", "-l", "1", "-w", "100", hostname]
  else:
    args = ['ping', '-c', '1', '-W', '1', hostname]
  ret_cod = subprocess.call(args, stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'))
  return ret_cod

def verify_hosts(base_ip):
  valid_hosts = []
  for i in range(80, 83): ##################### CHANGE TO (1, 255) BE COMPLETE
    print('Investigando host:', i)
    if (ping_code(base_ip + str(i)) == 0):
      valid_hosts.append(base_ip + str(i))
  return valid_hosts

def get_formated_ip(host):
  name = ''
  try:
    name = NM[host].hostname()
  except:
    print("Erro de hostname:", host)

  if not name:
    name = "Não possui nome disponível"
  return(f"{host} ({name})")

def get_formated_protocols(host):
  protocols = ''
  try:
    protocols = NM[host].all_protocols()
  except:
    print("Erro de protocols:", host)

  protocols = ', '.join(protocols)
  if not protocols:
    protocols = "Não possui protocolo disponível"
  return(f"Protocolos: {protocols}")

def get_formated_ports(host):
  ports_infos = []
  for proto in NM[host].all_protocols():
    ports_infos.append(f'Protocolo : {proto}\t')
    this_proto_ports_info = []
    for port in NM[host][proto].keys():
      port_info = NM[host][proto][port]
      text_port_info = f'Porta: {port}, Nome: {port_info["name"]}, Estado: {port_info["state"]}'
      this_proto_ports_info.append(text_port_info)
    ports_infos.append(" \n ".join(this_proto_ports_info))

  formated_ports_infos = " \n ".join(ports_infos)
  return(formated_ports_infos)

def fill_hosts_info(hosts):
  hosts_info = []
  for host in hosts :
    NM.scan(hosts = host, arguments='-n -PE -PA21,23,80,3389')
    print("Passei pelo nm", NM[host])
    host_info = {
      "ip": get_formated_ip(host),
      "state": NM[host]['status']['state'],
      "protocols": get_formated_protocols(host) or '',
      "ports": get_formated_ports(host)
    }
    hosts_info.append(host_info)
  return hosts_info

######################################################################################################

# MAIN
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
  if msg == "cpu":
    encoded_resp(cpu_spec(), cliente)
  if msg == "memory":
    encoded_resp(memory_spec(), cliente)
  if msg == "disk":
    encoded_resp(disk_spec(), cliente)
  if msg == "process":
    encoded_resp(process_spec(), cliente)
  if msg == "net":
    encoded_resp(net_spec(), cliente)
  if msg == "summary":
    encoded_resp(summary_spec(), cliente)
  
  if msg == "schedule":
    encoded_resp(schedule_spec(), cliente)
  if msg.split('?')[0] == "subnet":
    arg = msg.split('?')[1]
    encoded_resp(subnet_spec(arg), cliente)
  
  else:
    pass

tcp.close()
