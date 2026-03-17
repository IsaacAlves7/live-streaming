import time
import random
import threading
from prometheus_client import start_http_server, Gauge, Counter, Histogram
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Métricas Prometheus
# QoS
ingest_bitrate = Gauge('ingest_bitrate_bps', 'Bitrate do stream de ingestão')
transcoder_latency = Gauge('transcoder_latency_ms', 'Latência do transcodificador por segmento')
packager_segment_duration = Gauge('packager_segment_duration_seconds', 'Duração dos segmentos no packager')
cdn_response_time = Gauge('cdn_response_time_ms', 'Tempo de resposta da CDN')

# QoE
player_startup_time = Gauge('player_startup_time_ms', 'Tempo para o player iniciar playback')
player_buffer_level = Gauge('player_buffer_level_seconds', 'Nível do buffer do player')
player_rebuffering_ratio = Gauge('player_rebuffering_ratio', 'Proporção de rebuffering (0-1)')
player_bitrate_switch = Counter('player_bitrate_switches_total', 'Número de trocas de bitrate')

# Latência
latency_end_to_end = Gauge('latency_end_to_end_ms', 'Latência fim-a-fim (ingestão->player)')

# DRM
drm_license_acquisition_time = Histogram('drm_license_acquisition_time_ms', 'Tempo de aquisição de licença DRM', buckets=[50, 100, 200, 500, 1000, 2000])
drm_license_errors = Counter('drm_license_errors_total', 'Total de erros na aquisição de licença')

# Fallback
fallback_active = Gauge('fallback_active', 'Indica se o fallback está ativo (0 ou 1)')
fallback_switches = Counter('fallback_switches_total', 'Número total de trocas de fallback')

# Simulação de estados
current_bitrate = 5000000  # 5 Mbps
current_latency = 3000      # 3 segundos
fallback_on = 0
drm_error_rate = 0.02       # 2% de falhas

def simulate_ingest():
    """Simula variação de bitrate e geração de métricas de ingestão"""
    global current_bitrate
    while True:
        # Variação aleatória da bitrate (±10%)
        change = random.uniform(-0.1, 0.1) * current_bitrate
        current_bitrate = max(100000, min(20000000, current_bitrate + change))
        ingest_bitrate.set(current_bitrate)
        logging.info(f"Ingest bitrate: {current_bitrate/1e6:.2f} Mbps")
        time.sleep(5)

def simulate_transcoding():
    """Simula latência de transcodificação"""
    while True:
        # Latência entre 500ms e 5s, com picos ocasionais
        if random.random() < 0.05:  # 5% de chance de pico
            lat = random.uniform(5000, 10000)
        else:
            lat = random.uniform(500, 3000)
        transcoder_latency.set(lat)
        logging.info(f"Transcoder latency: {lat:.0f} ms")
        time.sleep(3)

def simulate_packager():
    """Simula duração de segmentos"""
    while True:
        dur = random.uniform(2, 10)  # segmentos de 2 a 10s
        packager_segment_duration.set(dur)
        time.sleep(2)

def simulate_cdn():
    """Simula tempo de resposta da CDN"""
    while True:
        resp = random.uniform(50, 500)  # 50-500ms
        if random.random() < 0.02:       # 2% de timeout simulado
            resp = random.uniform(2000, 5000)
        cdn_response_time.set(resp)
        time.sleep(2)

def simulate_player_qoe():
    """Simula métricas de QoE do player"""
    buffer_level = 10.0
    startup = 1500  # 1.5s
    rebuff_ratio = 0.0
    while True:
        # Simula variações no buffer
        buffer_delta = random.uniform(-2, 2)
        buffer_level = max(0, min(30, buffer_level + buffer_delta))
        player_buffer_level.set(buffer_level)

        # Rebuffering ocorre quando buffer baixo
        if buffer_level < 2 and random.random() < 0.1:
            rebuff_ratio += 0.01
            logging.warning("Rebuffering detected")
        rebuff_ratio = max(0, min(1, rebuff_ratio * 0.99))  # decai lentamente
        player_rebuffering_ratio.set(rebuff_ratio)

        # Startup time (ocorre uma vez, mas simulamos reinicializações)
        if random.random() < 0.01:
            startup = random.uniform(500, 5000)
            player_startup_time.set(startup)

        # Troca de bitrate ocasional
        if random.random() < 0.05:
            player_bitrate_switch.inc()
            logging.info("Bitrate switch")

        time.sleep(2)

def simulate_latency():
    """Simula latência fim-a-fim"""
    global current_latency
    while True:
        # Variação suave
        change = random.uniform(-100, 100)
        current_latency = max(500, min(10000, current_latency + change))
        latency_end_to_end.set(current_latency)
        logging.info(f"End-to-end latency: {current_latency:.0f} ms")
        time.sleep(4)

def simulate_drm():
    """Simula aquisição de licença DRM com falhas ocasionais"""
    while True:
        # Aquisição normal
        if random.random() > drm_error_rate:
            acquisition_time = random.uniform(50, 800)
            drm_license_acquisition_time.observe(acquisition_time)
            logging.info(f"DRM license acquired in {acquisition_time:.0f} ms")
        else:
            drm_license_errors.inc()
            logging.error("DRM license acquisition failed")
        time.sleep(10)

def simulate_fallback():
    """Simula sistema de fallback (troca entre primário e backup)"""
    global fallback_on
    while True:
        # A cada 30s, decide se muda estado
        if random.random() < 0.1:  # 10% de chance de troca
            fallback_on = 1 - fallback_on
            fallback_active.set(fallback_on)
            fallback_switches.inc()
            status = "ACTIVE" if fallback_on else "INACTIVE"
            logging.warning(f"Fallback switched to {status}")
        time.sleep(30)

def main():
    # Inicia servidor HTTP para expor métricas
    start_http_server(8000)
    logging.info("Métricas disponíveis em http://localhost:8000/metrics")

    # Inicia threads para cada simulador
    threads = [
        threading.Thread(target=simulate_ingest, daemon=True),
        threading.Thread(target=simulate_transcoding, daemon=True),
        threading.Thread(target=simulate_packager, daemon=True),
        threading.Thread(target=simulate_cdn, daemon=True),
        threading.Thread(target=simulate_player_qoe, daemon=True),
        threading.Thread(target=simulate_latency, daemon=True),
        threading.Thread(target=simulate_drm, daemon=True),
        threading.Thread(target=simulate_fallback, daemon=True),
    ]

    for t in threads:
        t.start()

    # Mantém o processo principal vivo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Encerrando...")

if __name__ == "__main__":
    main()