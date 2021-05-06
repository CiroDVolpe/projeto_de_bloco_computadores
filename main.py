import PySimpleGUI as sg
import socket
import psutil
import shutil
import platform
import cpuinfo
from collections import deque

RIGHT = '1111011100000011'
LEFT = '1111011100000010'
CPU_INFO = cpuinfo.get_cpu_info()
NUM_OF_CPUS = len(psutil.cpu_percent(interval=1, percpu=True))

sg.theme("LightBlue")

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

ip_layout = [ [sg.Text("Informações da Máquina")],
  [sg.Text(f"IP da máquina: {socket.gethostbyname(socket.gethostname())}")]
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
  ['cpu', cpu_layout],
  ['memory', memory_layout],
  ['disk', disk_layout],
  ['ip', ip_layout]
])

layout = [
  [
    sg.Column(cpu_layout, key='cpu'),
    sg.Column(memory_layout, visible=False, key='memory'),
    sg.Column(disk_layout, visible=False, key='disk'),
    sg.Column(ip_layout, visible=False, key='ip'),
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

def info_att(window, topic):
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

window = sg.Window('TP3 - Dados sobre o PC', layout, return_keyboard_events=True, use_default_focus=False)

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
      window['summary'].update(visible=False)

      if event == '<' or event_is_direction(event, 'LEFT'):
        window[current_topic()].update(visible=False)
        layout_carousel.rotate(1)
        window[current_topic()].update(visible=True)
      if event == '>' or event_is_direction(event, 'RIGHT'):
        window[current_topic()].update(visible=False)
        layout_carousel.rotate(-1)
        window[current_topic()].update(visible=True)
  
  info_att(window, 'summary' if window['summary'].visible else current_topic())


window.close()
