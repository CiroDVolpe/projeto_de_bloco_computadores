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
DATE_FORMAT = "%d/%m/%Y às %T"
TIME_FORMAT = '%H:%M:%S'
NUM_OF_PROCESS = 5
MAX_HOST_NUM = 10

######################################################################################################

# BASE
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.connect(DEST)

def send_to_server(topic):
  print("Enviando para o servidor:", topic)
  tcp.send(topic.encode('ascii'))

def get_from_server():
  received = tcp.recv(1024)
  loaded = pickle.loads(received)
  print(loaded)
  return loaded

def load_dict(info):
  return json.loads(info.replace("'", "\""))

######################################################################################################

# INITIAL
send_to_server('initial')
initial_info = load_dict(get_from_server())

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

# SUMMARY
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
  ['memory', memory_layout],
  ['disk', disk_layout]
])

layout = [
  [
    sg.Column(memory_layout, key='memory'),
    sg.Column(disk_layout, visible=False, key='disk'),
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


######################################################################################################

# ATT
def info_att(topic, args = ''):
  if topic == 'memory':
    att_memory()
  if topic == 'disk':
    att_disk()
  if topic == 'summary':
    att_summary()

######################################################################################################

# MAIN
window = sg.Window('TP8 - CLIENTE - Dados sobre o PC', layout, return_keyboard_events=True, use_default_focus=False)

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
      # if event == 'RODAR':
      #   schedule_finder()
      # if event == 'BUSCAR':
      #   args = values['EntradaIP']
      #   info_att(current_topic(), args)
  
  info_att('summary' if window['summary'].visible else current_topic())

######################################################################################################

# END
tcp.close()
window.close()
