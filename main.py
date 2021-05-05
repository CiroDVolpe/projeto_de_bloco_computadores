import PySimpleGUI as sg
import socket
import psutil
import shutil
import platform

sg.theme("LightBlue")

layout = [
  [
    sg.Text("Uso de memória (%)"),
    sg.ProgressBar(100, orientation='h', size=(20, 20), key='memory_percentage')
  ],
  [
    sg.Text(f"Uso de CPU, modelo: {platform.processor()} (%)"),
    sg.ProgressBar(100, orientation='h', size=(20, 20), key='cpu_percentage')
  ],
  [
    sg.Text("Uso de disco (%)"),
    sg.ProgressBar(100, orientation='h', size=(20, 20), key='disk_percentage')
  ],
  [sg.Text(f"IP da máquina: {socket.gethostbyname(socket.gethostname())}")],
  [sg.Cancel('Sair')]
]

window = sg.Window('TP2 - Dados sobre o PC', layout)

memory_bar = window['memory_percentage']
cpu_bar = window['cpu_percentage']
disk_bar = window['disk_percentage']

while True:
  event, values = window.read(timeout=1000)

  per_memory = psutil.virtual_memory().percent
  per_cpu = psutil.cpu_percent(interval=0)
  per_disco = int((shutil.disk_usage('/').used / shutil.disk_usage('/').total)*100)

  memory_bar.UpdateBar(per_memory)
  cpu_bar.UpdateBar(per_cpu)
  disk_bar.UpdateBar(per_disco)

  if event == 'Sair' or event == sg.WIN_CLOSED:
    break


window.close()
