import PySimpleGUI as sg
import socket
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
from collections import deque

RIGHT = '1111011100000011'
LEFT = '1111011100000010'
DATE_FORMAT = "%d/%m/%Y às %T"
TIME_FORMAT = '%H:%M:%S'
DIR = './files'
CPU_INFO = cpuinfo.get_cpu_info()
NUM_OF_CPUS = len(psutil.cpu_percent(interval=1, percpu=True))
NUM_OF_PROCESS = 5
FILES = os.listdir(DIR)
NM = PortScanner()
MAX_HOST_NUM = 10

start_time = call_time = exec_time = start_clock = exec_clock = 0

sg.theme("LightBlue")

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

def ping_code(hostname):
  if platform.system() == "Windows":
    args = ["ping", "-n", "2", "-l", "1", "-w", "100", hostname]
  else:
    args = ['ping', '-c', '1', '-W', '1', hostname]
  ret_cod = subprocess.call(args, stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'))
  return ret_cod

def verify_hosts(base_ip):
  host_validos = []
  for i in range(1, 254):
    if (ping_code(base_ip + str(i)) == 0):
      host_validos.append(base_ip + str(i))
  return host_validos

def get_formated_hostname(host):
  name = ''
  try:
    name = NM[host].hostname()
  except:
    print("Erro de hostname:", host)

  if not name:
    name = "Não possui nome disponível"
  return(f"IP: {host} ({name})")
  
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

def get_formated_ports_info(host):
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

def getListOfProcessSortedByMemory(num):
  listOfProcObjects = []

  for proc in psutil.process_iter():
    try:
      pinfo = proc.as_dict(attrs=['pid', 'name', 'username'])
      pinfo['vms'] = proc.memory_info().vms / (1024 * 1024)

      listOfProcObjects.append(pinfo)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
      pass

  listOfProcObjects = sorted(listOfProcObjects, key=lambda procObj: procObj['vms'], reverse=True)

  return listOfProcObjects[:num]

PROCESSES = getListOfProcessSortedByMemory(NUM_OF_PROCESS)

def cpu_percent(pid):
  test_list = []
  for i in range(5):
    p = psutil.Process(pid)
    p_cpu = p.cpu_percent(interval=0.1)
    test_list.append(p_cpu)
  return float(sum(test_list))/len(test_list)

def format_file_path(file):
  return(DIR + '/' + file)

files_layout = [ [sg.Text("Informações de Arquivos e Diretórios")],
  [
    sg.Text(f"Nome do diretório atual: {os.getcwd()}")
  ],
  [sg.Text("Dados do escalonamento de 1 segundo com sleep de 1 segundo da função de verificação de arquivos: ")],
  [sg.Text("Tempo inicial: CLIQUE EM RODAR PARA RECEBER UM VALOR", key="start_time_text")],
  [sg.Text("Tempo chamada: CLIQUE EM RODAR PARA RECEBER UM VALOR", key="call_time_text")],
  [sg.Text("Tempo final da execução: CLIQUE EM RODAR PARA RECEBER UM VALOR", key="exec_time_text")],
  [sg.Text("Duração da chamada: CLIQUE EM RODAR PARA RECEBER UM VALOR", key="proc_time_text")],
  [sg.Text("Quantidade total de clocks para a realização do inicio até o final: CLIQUE EM RODAR PARA RECEBER UM VALOR", key="clock_time_text")],
  [sg.Button('RODAR')]
]+ \
[
  [
    sg.Text(f"Nome do arquivo: {FILES[x]}"),
    sg.Text(f"Tamanho: {os.path.getsize(format_file_path(FILES[x]))} bytes"),
    sg.Text(f"Data de criação: {datetime.fromtimestamp(os.stat(format_file_path(FILES[x])).st_ctime).strftime(DATE_FORMAT)}"),
    sg.Text(f"Data de modificação: {datetime.fromtimestamp(os.stat(format_file_path(FILES[x])).st_mtime).strftime(DATE_FORMAT)}"),
    sg.Text(f"Tipo: {FILES[x].split('.')[1]}")
  ] for x in range(len(FILES))
] 

process_layout = [ [sg.Text("Informações de Processos")],
  [
    sg.Text(f"PID do processo do Python: {os.getpid()}"),
    sg.Text(f"Porcentagem do processador no processo do programa: {cpu_percent(os.getpid())}", key="python_cpu_percent")
  ]
]+ \
[
  [
    sg.Text(f"PID: {PROCESSES[x]['pid']}", key=f"process_pid-{x}"),
    sg.Text(f"Nome do executável: {PROCESSES[x]['name']}", key=f"process_name-{x}"),
    sg.Text(f"Consumo de processamento: {cpu_percent(PROCESSES[x]['pid'])} (%)", key=f"process_cpu_percent-{x}"),
    sg.Text(f"Consumo de memória: {PROCESSES[x]['vms']}", key=f"process_vms-{x}"),
    sg.Text(f"Usuário: {PROCESSES[x]['username']}", key=f"process_username-{x}")
  ] for x in range(NUM_OF_PROCESS)
] 


cpu_layout = [ [sg.Text("Informações do Processador")],
  [
    sg.Text(f"Nome e modelo de CPU: {platform.platform()}")
  ],
  [
    sg.Text(f"Tipo de arquitetura: {CPU_INFO['arch']}") 
  ],
  [
    sg.Text(f"Palavra do processador (bits): {CPU_INFO['bits']}")
  ],
  [
    sg.Text(f"Frequencia min e max da CPU (MHz): {psutil.cpu_freq().min} || {psutil.cpu_freq().max}")
  ],
  [
    sg.Text(f"Frequencia atual da CPU (MHz): {psutil.cpu_freq().current}")
  ],
  [
    sg.Text(f"Numero total de núcleos físicos: {psutil.cpu_count(logical=False)}")
  ],
  [
    sg.Text(f"Numero total de núcleos lógicos: {psutil.cpu_count()}")
  ]
]+ \
[
  [
    sg.Text(f"Uso de CPU {x+1} (%)"),
    sg.ProgressBar(100, orientation='h', size=(20, 20), key=f'cpu_percentage-{x}')
  ] for x in range(NUM_OF_CPUS)
] 

memory_layout = [ [sg.Text("Informações da Memória")],
  [
    sg.Text("Uso de memória (%)"),
    sg.ProgressBar(100, orientation='h', size=(20, 20), key='memory_percentage')
  ]
]

disk_layout = [ [sg.Text("Informações do Disco")],
  [
    sg.Text("Uso de disco (%)"),
    sg.ProgressBar(100, orientation='h', size=(20, 20), key='disk_percentage')
  ]
]

ip_layout = [ [sg.Text("Informações da SubRede")],
  [sg.Text(f"IP da máquina atual: {socket.gethostbyname(socket.gethostname())}")],
  [
    sg.Text("Digite um IP"),
    sg.InputText(key='EntradaIP'),
    sg.Button('BUSCAR')
  ],
  [
    sg.Text("Esse processo pode demorar!"),
  ]
]+ \
[
  [
    sg.Text(f"HOST {x + 1}", key=f"host-{x}", visible=False),
    sg.Text("IP: 000.000.000.000 Placeholder (Nome Placeholder Nome Placeholder Nome Placeholder Nome Placeholder)", key=f"ip_host-{x}", visible=False),
    sg.Text("Estado: Estado Placeholder", key=f"state_host-{x}", visible=False),
    sg.Text("Protocolos disponiveis: Protocolos Placeholder", key=f"protocols_host-{x}", visible=False),
    sg.Multiline("Portas disponíveis e suas infos: Portas Placeholder Estado da Porta: Estado Placeholder", key=f"ports_host-{x}",disabled=True, visible=False)
  ] for x in range(MAX_HOST_NUM)
]

net_layout = [ [sg.Text("Informações das Conexões em Rede")],
  [
    sg.Text("Interfaces conectadas"),
    sg.Multiline("Conexões e seus detalhes placeholder", key="net_interfaces_info", size=(100, 20), disabled=True, visible=False)
  ],
  [
    sg.Text("Uso de dados de rede por interface"),
    sg.Multiline("Uso de dados de rede por interface placeholder", key=f"net_interfaces_ios", size=(100, 20), disabled=True, visible=False)
  ],
  [
    sg.Text("Uso de dados de rede por processo"),
    sg.Multiline("Uso de dados de rede por processo placeholder", key=f"net_processes", size=(100, 20), disabled=True, visible=False)
  ]
]

summary_layout = [ [sg.Text("Resumo")],
  [
    sg.Text(f"Uso de CPU (%)"),
    sg.ProgressBar(100, orientation='h', size=(20, 20), key='summary_cpu_percentage')
  ],
  [
    sg.Text("Uso de memória (%)"),
    sg.ProgressBar(100, orientation='h', size=(20, 20), key='summary_memory_percentage')
  ],
  [
    sg.Text("Uso de disco (%)"),
    sg.ProgressBar(100, orientation='h', size=(20, 20), key='summary_disk_percentage')
  ],
  [sg.Text(f"IP da máquina: {socket.gethostbyname(socket.gethostname())}")]
]

layout_carousel = deque([
  ['files' ,files_layout],
  ['process' ,process_layout],
  ['cpu', cpu_layout],
  ['memory', memory_layout],
  ['disk', disk_layout],
  ['ip', ip_layout],
  ['net', net_layout]
])

layout = [
  [
    sg.Column(files_layout, key='files'),
    sg.Column(process_layout, key='process', visible=False),
    sg.Column(cpu_layout, key='cpu', visible=False),
    sg.Column(memory_layout, visible=False, key='memory'),
    sg.Column(disk_layout, visible=False, key='disk'),
    sg.Column(ip_layout, visible=False, key='ip'),
    sg.Column(net_layout, visible=False, key='net'),
    sg.Column(summary_layout, visible=False, key='summary'),
  ],
  [sg.Button('<'), sg.Text('Aperte ESPAÇO para ver ou sair do resumo.'), sg.Button('>'), sg.Cancel('Sair')]
]

def current_layout():
  return layout_carousel[0][1]

def current_topic():
  return layout_carousel[0][0]

def event_is_direction(event, direction):
  return ' '.join(format(ord(x), 'b') for x in event) == eval(direction)

def info_att(window, topic, args = ''):
  if topic == 'net':
    net_interfaces_info = window["net_interfaces_info"]
    if not net_interfaces_info.visible:
      interfaces = psutil.net_if_addrs()
      interfaces_text = ""

      for i in interfaces:
        nome = str(i)
        interfaces_text = interfaces_text + f"{nome}: \n"
        for info in interfaces[nome]:
          interfaces_text = interfaces_text + f"\t Endereço: {info.address} | Mascara de rede: {info.netmask} | Familia: {obtem_nome_familia(info.family)} \n"

      net_interfaces_info.Update(f"{interfaces_text}")
      net_interfaces_info.update(visible=True)


    io_status = psutil.net_io_counters(pernic=True)
    ios_text = ""
    for i in io_status:
      ios_text = ios_text + f"{str(i)} \n"
      info = io_status[str(i)]
      ios_text = ios_text + f"\t BYTES: Envidaos: {info.bytes_sent} | Recebidos: {info.bytes_recv} \n\t PACOTES: Enviados: {info.packets_sent} | Recebidos: {info.packets_recv} \n"
    
    net_interfaces_ios = window["net_interfaces_ios"]
    net_interfaces_ios.Update(f"{ios_text}")
    net_interfaces_ios.update(visible=True)


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
  
    net_processes = window["net_processes"]
    net_processes.Update(f"{pids_text}")
    net_processes.update(visible=True)

  if topic == 'ip':
    if args != '':
      ip_lista = args.split(".")
      rede = ".".join(ip_lista[0:3]) + "."
      hosts = verify_hosts(rede)
      hosts_len = len(hosts)
      for x in range(hosts_len):
        host = hosts[x]
        NM.scan(host)

        host_num = window[f"host-{x}"]
        host_num.update(visible=True)

        ip_host = window[f"ip_host-{x}"]
        formated_name = get_formated_hostname(host)
        ip_host.Update(f"{formated_name}")
        ip_host.update(visible=True)

        state_host = window[f"state_host-{x}"]
        state = NM[host]['status']['state']
        state_host.Update(f"Estado: {state}")
        state_host.update(visible=True)

        protocols_host = window[f"protocols_host-{x}"]
        formated_protocols = get_formated_protocols(host)
        protocols_host.Update(f"{formated_protocols}")
        protocols_host.update(visible=True)

        ports_host = window[f"ports_host-{x}"]
        formated_ports_info = get_formated_ports_info(host)
        ports_host.Update(f"{formated_ports_info}")
        ports_host.update(visible=True)

  if topic == 'summary':
    summary_cpu_bar = window['summary_cpu_percentage']
    summary_memory_bar = window['summary_memory_percentage']
    summary_disk_bar = window['summary_disk_percentage']

    per_cpu = psutil.cpu_percent(interval=0)
    per_memory = psutil.virtual_memory().percent
    per_disco = int((shutil.disk_usage('/').used / shutil.disk_usage('/').total)*100)

    summary_cpu_bar.UpdateBar(per_cpu)
    summary_memory_bar.UpdateBar(per_memory)
    summary_disk_bar.UpdateBar(per_disco)

  if topic == 'cpu':
    for x in range(NUM_OF_CPUS):
      cpu_bar = window[f'cpu_percentage-{x}']

      per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)[x]

      cpu_bar.UpdateBar(per_cpu)
  if topic == 'memory':
    memory_bar = window['memory_percentage']

    per_memory = psutil.virtual_memory().percent

    memory_bar.UpdateBar(per_memory)
  if topic == 'disk':
    disk_bar = window['disk_percentage']

    per_disco = int((shutil.disk_usage('/').used / shutil.disk_usage('/').total)*100)

    disk_bar.UpdateBar(per_disco)
  if topic == 'files':
    if start_time != 0:
      start_time_field = window['start_time_text']
      start_time_field.Update(f"Tempo inicial: {start_time}")

      call_time_field = window['call_time_text']
      call_time_field.Update(f"Tempo chamada (c/ delay): {call_time}")

      exec_time_field = window['exec_time_text']
      exec_time_field.Update(f"Tempo final da execução (c/ sleep): {exec_time}")

      proc_time_field = window['proc_time_text']
      exec_call_time_diff = datetime.strptime(exec_time, TIME_FORMAT) - datetime.strptime(call_time, TIME_FORMAT)
      proc_time_field.Update(f"Duração da chamada (c/ sleep): {exec_call_time_diff}")

      clock_time_field = window['clock_time_text']
      clock_time_field.Update(f"Quantidade total de clocks para a realização do inicio até o final: {round(exec_clock - start_clock, 7)} segundo")

  if topic == 'process':
    python_cpu_text = window["python_cpu_percent"]
    python_cpu_text.Update(f"Porcentagem do processador no processo do programa: {cpu_percent(os.getpid())}")

    PROCESSES = getListOfProcessSortedByMemory(NUM_OF_PROCESS)
    for x in range(NUM_OF_PROCESS):
      process_pid = window[f"process_pid-{x}"]
      process_name = window[f"process_name-{x}"]
      process_cpu_percent = window[f"process_cpu_percent-{x}"]
      process_vms = window[f"process_vms-{x}"]
      process_username = window[f"process_username-{x}"]

      process_pid.Update(f"PID: {PROCESSES[x]['pid']}")
      process_name.Update(f"Nome do executável: {PROCESSES[x]['name']}")
      process_cpu_percent.Update(f"Consumo de processamento: {cpu_percent(PROCESSES[x]['pid'])} (%)")
      process_vms.Update(f"Consumo de memória: {PROCESSES[x]['vms']}")
      process_username.Update(f"Usuário: {PROCESSES[x]['username']}")

window = sg.Window('TP7 - Dados sobre o PC', layout, return_keyboard_events=True, use_default_focus=False)

while True:
  event, values = window.read(timeout=1000)

  if event == 'Sair' or event == sg.WIN_CLOSED:
    break
     
  if event != '__TIMEOUT__':
    if event == ' ':
      if window['summary'].visible:
        window['summary'].update(visible=False)
        window[current_topic()].update(visible=True)
      else:
        window[current_topic()].update(visible=False)
        window['summary'].update(visible=True)
    else:
      if window['summary'].visible:
        window['summary'].update(visible=False)

      if event == '<' or event_is_direction(event, 'LEFT'):
        window[current_topic()].update(visible=False)
        layout_carousel.rotate(1)
        window[current_topic()].update(visible=True)
      if event == '>' or event_is_direction(event, 'RIGHT'):
        window[current_topic()].update(visible=False)
        layout_carousel.rotate(-1)
        window[current_topic()].update(visible=True)
      if event == 'RODAR':
        schedule_finder()
      if event == 'BUSCAR':
        args = values['EntradaIP']
        info_att(window, current_topic(), args)
  
  info_att(window, 'summary' if window['summary'].visible else current_topic())


window.close()
