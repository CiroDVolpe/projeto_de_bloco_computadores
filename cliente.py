import socket, pickle, json
import PySimpleGUI as sg
from collections import deque

print("Bem vindo ao cliente tcp do projeto de bloco!")

sg.theme("LightBlue")

HOST = socket.gethostname()
PORT = 8888
DEST = (HOST, PORT)

RIGHT = '1111011100000011'
LEFT = '1111011100000010'

######################################################################################################

# BASE
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.connect(DEST)

def send_to_server(topic):
  print("Enviando para o servidor:", topic)
  tcp.send(topic.encode('ascii'))

def get_from_server():
  received = tcp.recv(8192)
  loaded = pickle.loads(received)
  print(loaded)
  return loaded

def load_dict(info):
  return json.loads(info.replace("'", "\""))

######################################################################################################

# INITIAL
send_to_server('initial')
initial_info = load_dict(get_from_server())

initial_cpu_info = initial_info["cpu"]
initial_files_info = initial_info["files"]
initial_process_info = initial_info["process"]
initial_ip_info = initial_info["ip"]
initial_net_info = initial_info["net"]

######################################################################################################

# CPU
cpu_layout = [ [sg.Text("Informações do Processador")],
  [
    sg.Text(f"Nome e modelo de CPU: {initial_cpu_info['name']}")
  ],
  [
    sg.Text(f"Tipo de arquitetura: {initial_cpu_info['arch']}") 
  ],
  [
    sg.Text(f"Palavra do processador (bits): {initial_cpu_info['bits']}")
  ],
  [
    sg.Text(f"Frequencia min e max da CPU (MHz): {initial_cpu_info['freq_min']} || {initial_cpu_info['freq_max']}")
  ],
  [
    sg.Text(f"Frequencia atual da CPU (MHz): {initial_cpu_info['freq_cur']}")
  ],
  [
    sg.Text(f"Numero total de núcleos físicos: {initial_cpu_info['fis_cores']}")
  ],
  [
    sg.Text(f"Numero total de núcleos lógicos: {initial_cpu_info['log_cores']}")
  ]
]+ \
[
  [
    sg.Text(f"Uso de CPU {x+1} (%)"),
    sg.ProgressBar(100, orientation='h', size=(20, 20), key=f'cpu_percentage-{x}')
  ] for x in range(initial_cpu_info["num_of_cpus"])
]

def att_cpu():
  send_to_server('cpu')
  cpus = load_dict(get_from_server())
  for x in range(initial_cpu_info["num_of_cpus"]):
    cpu_bar = window[f'cpu_percentage-{x}']
    per_cpu = cpus[x]
    cpu_bar.UpdateBar(per_cpu)

######################################################################################################

# MEMORY
memory_layout = [ [sg.Text("Informações da Memória")],
  [
    sg.Text("Uso de memória (%)"),
    sg.ProgressBar(100, orientation='h', size=(20, 20), key='memory_percentage')
  ]
]

def att_memory():
  send_to_server('memory')
  memory_bar = window['memory_percentage']
  memory_info = get_from_server()
  per_memory = memory_info
  memory_bar.UpdateBar(per_memory)

######################################################################################################

# DISK
disk_layout = [ [sg.Text("Informações do Disco")],
  [
    sg.Text("Uso de disco (%)"),
    sg.ProgressBar(100, orientation='h', size=(20, 20), key='disk_percentage')
  ]
]

def att_disk():
  send_to_server('disk')
  disk_bar = window['disk_percentage']
  disk_info = get_from_server()
  per_disk = disk_info
  disk_bar.UpdateBar(per_disk)

######################################################################################################

# FILES
files_layout = [ [sg.Text("Informações de Arquivos e Diretórios")],
  [
    sg.Text(f"Nome do diretório atual: {initial_files_info['dir']}")
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
    sg.Text(f"Nome do arquivo: {initial_files_info['files_specs'][x]['name']}"),
    sg.Text(f"Tamanho: {initial_files_info['files_specs'][x]['size']} bytes"),
    sg.Text(f"Data de criação: {initial_files_info['files_specs'][x]['creation_date']}"),
    sg.Text(f"Data de modificação: {initial_files_info['files_specs'][x]['modified_date']}"),
    sg.Text(f"Tipo: {initial_files_info['files_specs'][x]['type']}")
  ] for x in range(initial_files_info['num_of_files'])
]

def att_schedule():
  send_to_server('schedule')

  start_time_field = window['start_time_text']
  call_time_field = window['call_time_text']
  exec_time_field = window['exec_time_text']
  proc_time_field = window['proc_time_text']
  clock_time_field = window['clock_time_text']

  schedule_info = load_dict(get_from_server())

  start_time = schedule_info['start_time']
  call_time = schedule_info['call_time']
  exec_time = schedule_info['exec_time']
  exec_diff_time = schedule_info['exec_diff_time']
  clock_diff_time = schedule_info['clock_diff_time']

  start_time_field.Update(f"Tempo inicial: {start_time}")
  call_time_field.Update(f"Tempo chamada (c/ delay): {call_time}")
  exec_time_field.Update(f"Tempo final da execução (c/ sleep): {exec_time}")
  proc_time_field.Update(f"Duração da chamada (c/ sleep): {exec_diff_time}")
  clock_time_field.Update(f"Quantidade total de clocks para a realização do inicio até o final: {clock_diff_time} segundo")

######################################################################################################

# PROCESS
process_layout = [ [sg.Text("Informações de Processos (Servidor)")],
  [
    sg.Text(f"PID do processo do Python: {initial_process_info['pid']}"),
    sg.Text(f"Porcentagem do processador no processo do programa: {initial_process_info['perc']}", key="python_cpu_percent")
  ]
]+ \
[
  [
    sg.Text(f"PID: CARREGANDO LISTA, POR FAVOR ESPERE", key=f"process_pid-{x}"),
    sg.Text(f"Nome do executável: CARREGANDO LISTA, POR FAVOR ESPERE", key=f"process_name-{x}"),
    sg.Text(f"Consumo de processamento: CARREGANDO LISTA, POR FAVOR ESPERE", key=f"process_cpu_percent-{x}"),
    sg.Text(f"Consumo de memória: CARREGANDO LISTA, POR FAVOR ESPERE", key=f"process_vms-{x}"),
    sg.Text(f"Usuário: CARREGANDO LISTA, POR FAVOR ESPERE", key=f"process_username-{x}")
  ] for x in range(initial_process_info['num_of_processes'])
]

def att_process():
  send_to_server('process')
  processes = load_dict(get_from_server())

  python_cpu_text = window["python_cpu_percent"]
  python_cpu_percent = processes["my_cpu_percent"]
  python_cpu_text.Update(f"Porcentagem do processador no processo do programa: {python_cpu_percent}")

  for x in range(initial_process_info["num_of_processes"]):
    process_pid = window[f"process_pid-{x}"]
    process_name = window[f"process_name-{x}"]
    process_cpu_percent = window[f"process_cpu_percent-{x}"]
    process_vms = window[f"process_vms-{x}"]
    process_username = window[f"process_username-{x}"]

    pid = processes['processes'][x]['pid']
    name = processes['processes'][x]['name']
    cpu_percent = processes['processes'][x]['cpu_percent']
    memory_usage = processes['processes'][x]['memory_usage']
    username = processes['processes'][x]['username']

    process_pid.Update(f"PID: {pid}")
    process_name.Update(f"Nome do executável: {name}")
    process_cpu_percent.Update(f"Consumo de processamento: {cpu_percent} (%)")
    process_vms.Update(f"Consumo de memória: {memory_usage}")
    process_username.Update(f"Usuário: {username}")

######################################################################################################

# NET
interfaces = initial_net_info["interfaces"]
usage_per_interface = initial_net_info["usage_per_interface"]
usage_per_process = initial_net_info["usage_per_process"]

net_layout = [ [sg.Text("Informações das Conexões em Rede")],
  [
    sg.Text("Interfaces conectadas"),
    sg.Multiline(f'{interfaces}', size=(100, 20), disabled=True)
  ],
  [
    sg.Text("Uso de dados de rede por interface"),
    sg.Multiline(f'{usage_per_interface}', size=(100, 20), key=f"net_interfaces_ios", disabled=True)
  ],
  [
    sg.Text("Uso de dados de rede por processo"),
    sg.Multiline(f'{usage_per_process}', size=(100, 20), key=f"net_processes", disabled=True)
  ]
]

def att_net():
  send_to_server('net')

  net_interfaces_ios = window['net_interfaces_ios']
  net_processes = window['net_processes']

  summary_info = load_dict(get_from_server())

  usage_per_interface = summary_info["usage_per_interface"]
  usage_per_process = summary_info["usage_per_process"]

  net_interfaces_ios.Update(usage_per_interface)
  net_processes.Update(usage_per_process)

######################################################################################################

# IP
ip_layout = [ [sg.Text("Informações da SubRede")],
  [sg.Text(f"IP da máquina atual: {initial_ip_info['my_ip']}")],
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
    sg.Text(f"HOST {x + 1}", key=f"subnet_host-{x}", visible=False),
    sg.Text("IP: 000.000.000.000 Placeholder (Nome Placeholder Nome Placeholder Nome Placeholder Nome Placeholder)", key=f"subnet_host_ip-{x}", visible=False),
    sg.Text("Estado: Estado Placeholder", key=f"subnet_host_state-{x}", visible=False),
    sg.Text("Protocolos disponiveis: Protocolos Placeholder", key=f"subnet_host_protocols-{x}", visible=False),
    sg.Text("Portas disponíveis e suas infos:", key=f"subnet_host_ports_text-{x}", visible=False),
    sg.Multiline("Portas disponíveis e suas infos: Portas Placeholder Estado da Porta: Estado Placeholder", key=f"subnet_host_ports-{x}",disabled=True, visible=False)
  ] for x in range(initial_ip_info["max_num_hosts"])
]

def att_subnet(args):
  send_to_server(f'subnet?{args}')

  subnet_info = load_dict(get_from_server())

  for x in range(subnet_info["len"]):
    subnet_host = window[f"subnet_host-{x}"]
    subnet_host_ip = window[f"subnet_host_ip-{x}"]
    subnet_host_state = window[f"subnet_host_state-{x}"]
    subnet_host_protocols = window[f"subnet_host_protocols-{x}"]
    subnet_host_ports_text = window[f"subnet_host_ports_text-{x}"]
    subnet_host_ports = window[f"subnet_host_ports-{x}"]

    ip = subnet_info['hosts'][x]['ip']
    state = subnet_info['hosts'][x]['state']
    protocols = subnet_info['hosts'][x]['protocols']
    ports = subnet_info['hosts'][x]['ports']

    subnet_host.Update(f"HOST {x + 1}")
    subnet_host.update(visible=True)

    subnet_host_ip.Update(f"IP: {ip}")
    subnet_host_ip.update(visible=True)

    subnet_host_state.Update(f"Estado:: {state}")
    subnet_host_state.update(visible=True)

    subnet_host_protocols.Update(f"Protocolos disponiveis: {protocols}")
    subnet_host_protocols.update(visible=True)

    subnet_host_ports.Update(f"{ports}")
    subnet_host_ports_text.update(visible=True)
    subnet_host_ports.update(visible=True)

######################################################################################################

# SUMMARY
summary_layout = [[sg.Text("Resumo")],
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
  [sg.Text(f"IP da máquina: {initial_info['summary']['ip']}")]
]

def att_summary():
  send_to_server('summary')

  summary_cpu_bar = window['summary_cpu_percentage']
  summary_memory_bar = window['summary_memory_percentage']
  summary_disk_bar = window['summary_disk_percentage']

  summary_info = load_dict(get_from_server())

  per_cpu = summary_info["cpu"]
  per_memory = summary_info["memory"]
  per_disk = summary_info["disk"]

  summary_cpu_bar.UpdateBar(per_cpu)
  summary_memory_bar.UpdateBar(per_memory)
  summary_disk_bar.UpdateBar(per_disk)


######################################################################################################

# LAYOUT
layout_carousel = deque([
  ['cpu', cpu_layout],
  ['memory', memory_layout],
  ['disk', disk_layout],
  ['files', files_layout],
  ['process', process_layout],
  ['net', net_layout],
  ['ip', ip_layout]
])

layout = [
  [
    sg.Column(cpu_layout, key='cpu'),
    sg.Column(memory_layout, key='memory', visible=False),
    sg.Column(disk_layout, key='disk', visible=False),
    sg.Column(files_layout, key='files', visible=False),
    sg.Column(process_layout, key='process', visible=False),
    sg.Column(net_layout, key='net', visible=False),
    sg.Column(ip_layout, key='ip', visible=False),
    sg.Column(summary_layout, key='summary', visible=False),
  ],
  [sg.Button('<'), sg.Text('Aperte ESPAÇO para ver ou sair do resumo.'), sg.Button('>'), sg.Cancel('Sair')]
]

def current_layout():
  return layout_carousel[0][1]

def current_topic():
  return layout_carousel[0][0]

def event_is_direction(event, direction):
  return ' '.join(format(ord(x), 'b') for x in event) == eval(direction)


######################################################################################################

# ATT
def info_att(topic, args = ''):
  if topic == 'cpu':
    att_cpu()
  if topic == 'memory':
    att_memory()
  if topic == 'disk':
    att_disk()
  if topic == 'files':
    pass
  if topic == 'process':
    att_process()
  if topic == 'net':
    att_net()
  if topic == 'ip':
    pass
  if topic == 'summary':
    att_summary()

######################################################################################################

# MAIN
window = sg.Window('TP9 - CLIENTE - Dados sobre o PC', layout, return_keyboard_events=True, use_default_focus=False)

while True:
  event, values = window.read(timeout=1000)

  if event == 'Sair' or event == sg.WIN_CLOSED:
    tcp.sendto('exit'.encode('ascii'), DEST)
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
        att_schedule()
      if event == 'BUSCAR':
        args = values['EntradaIP']
        att_subnet(args)
  
  info_att('summary' if window['summary'].visible else current_topic())

######################################################################################################

# END
tcp.close()
window.close()
