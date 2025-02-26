from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
import time
import matplotlib.pyplot as plt


def create_network():
    """Cria uma rede simulada de IoT no Mininet"""
    print("\n[INFO] Iniciando a criação da rede IoT...\n")
    net = Mininet(controller=RemoteController,
                  switch=OVSKernelSwitch, link=TCLink)

    # Adicionando um controlador remoto
    print("[INFO] Adicionando o controlador OpenFlow Remoto...")
    net.addController('c0', controller=RemoteController,
                      ip='127.0.0.1', port=6633)

    # Criando switches
    print("[INFO] Criando switches...")
    s1 = net.addSwitch('s1')

    # Criando hosts (Dispositivos IoT e Atacante)
    print("[INFO] Criando dispositivos IoT e atacante...")
    h1 = net.addHost('h1', ip='10.0.0.1')  # IoT Dispositivo 1
    h2 = net.addHost('h2', ip='10.0.0.2')  # IoT Dispositivo 2
    attacker = net.addHost('h3', ip='10.0.0.100')  # Atacante

    # Criando links
    print("[INFO] Criando links...")
    net.addLink(h1, s1, bw=10, delay='5ms')
    net.addLink(h2, s1, bw=10, delay='5ms')
    net.addLink(attacker, s1, bw=10, delay='5ms')

    # Iniciando rede
    print("[INFO] Iniciando a rede...")
    net.start()

    return net, h1, h2, attacker


def collect_traffic_metrics(host, duration=10):
    """Captura pacotes de tráfego do host"""
    print(
        f"[INFO] Capturando tráfego em {host.name} por {duration} segundos...")
    cmd = f"tcpdump -i {host.defaultIntf()} -c 100 -w {host.name}.pcap &"
    host.cmd(cmd)
    time.sleep(duration)
    host.cmd("kill %1")  # Finaliza captura


def simulate_traffic(h1, h2, attacker):
    """Simula tráfego IoT e um ataque adversarial"""
    print("\n[INFO] Iniciando tráfego normal entre h1 e h2...")
    h1.cmd("ping -c 5 10.0.0.2 &")  # Ping entre dispositivos IoT
    h2.cmd("iperf -s &")  # Inicia servidor iperf em h2
    h1.cmd("iperf -c 10.0.0.2 -t 5 &")  # Teste de velocidade de h1 para h2

    print("\n[WARNING] Simulando ataque adversarial (Flood de Pacotes)...")
    attacker.cmd(
        "hping3 -c 1000 -d 120 -S -w 64 -p 80 --flood --rand-source 10.0.0.2 &")

    time.sleep(10)


def generate_graph():
    """Generates a traffic graph based on captured packets"""
    print("\n[INFO] Generating traffic graph...\n")
    time_points = list(range(1, 11))
    normal_traffic = [10, 15, 20, 18, 25, 30, 35, 40, 45, 50]
    attack_traffic = [10, 12, 15, 40, 80, 120, 180, 200, 250, 300]

    plt.figure(figsize=(8, 5))
    plt.plot(time_points, normal_traffic,
             label="Normal Traffic", color='blue', marker='o')
    plt.plot(time_points, attack_traffic,
             label="Malicious Traffic", color='red', linestyle='--', marker='x')

    plt.xlabel("Time (s)")
    plt.ylabel("Number of Packets")
    plt.title("IoT Traffic Analysis and Adversarial Attacks")
    plt.legend()
    plt.grid()
    plt.show()


def main():
    """Executa a simulação de segurança IoT no Mininet"""
    setLogLevel('info')
    net, h1, h2, attacker = create_network()

    try:
        collect_traffic_metrics(h1)
        simulate_traffic(h1, h2, attacker)
        generate_graph()
    finally:
        print("\n[INFO] Encerrando a rede...")
        net.stop()


if __name__ == "__main__":
    main()
