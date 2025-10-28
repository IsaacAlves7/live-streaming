# 📹 Live Streaming
<img src="https://github.com/user-attachments/assets/e110d977-238e-4ed2-98a2-a2e86e6f25cb" align="right" height="77">

**Live Streaming**, do ponto de vista da ciência da computação, é essencialmente uma estratégia de transmissão contínua de dados, na qual áudio e vídeo são capturados, comprimidos, enviados pela rede em pacotes e reconstruídos do outro lado com o mínimo de atraso possível. A chave aqui não é apenas transmitir, mas transmitir enquanto ainda está acontecendo, o que exige sincronização, protocolos adequados, buffers inteligentes e controle de latência.

Tudo começa na **captura do sinal**. Uma câmera ou placa de captura gera um fluxo bruto de vídeo (RAW), que é extremamente pesado. Esse dado não pode simplesmente ser enviado pela internet; ele precisa ser **codificado**. A codificação é a aplicação de um **codec** (como H.264, H.265 ou VP9 para vídeo; AAC ou Opus para áudio), que transforma milhares de informações por segundo em um fluxo comprimido, de modo que ainda seja possível reconstruí-lo com qualidade aceitável no destino. Esse processo pode ser realizado pela GPU, pela CPU, ou por chips dedicados (hardware encoders), sendo que cada um afeta a latência, a qualidade e o desempenho.

Depois de codificado, o fluxo é embalado em um **container** ― formatos como MP4, FLV, WEBM, MKV ― mas no streaming ao vivo, o vídeo é geralmente segmentado em pequenas **chuncks** ou pacotes (ex: 2 segundos cada). Isso permite que o receptor comece a exibir antes mesmo de receber tudo. Aqui entra a essência da diferença entre streaming e download: o cliente não espera o arquivo completo; ele **consome enquanto recebe**.

Agora entra a rede: o fluxo segue por protocolos. No streaming ao vivo, não se usa apenas HTTP tradicional. Existem protocolos especializados como **RTMP**, que envia o vídeo continuamente para um servidor central; esse servidor, por sua vez, converte e redistribui em protocolos como **HLS** (HTTP Live Streaming) ou **DASH**. O motivo dessa conversão é simples: RTMP é bom para ingestão de baixa latência, enquanto HLS é melhor para entrega global resistente a quedas de conexão. HLS funciona como uma espécie de “playlist indexada” (um .m3u8) que aponta para pequenos trechos de vídeo que o player vai baixando e exibindo conforme chega.

Só que aí entra o desafio real: **latência**. O delay entre o que a câmera grava e o que o espectador vê pode ser de milissegundos a dezenas de segundos. Quanto menor a janela do buffer (a fila temporária de pacotes antes da reprodução), mais “ao vivo” fica a transmissão — mas menos tolerante a oscilações de rede. Quanto maior o buffer, mais estável, mas menos instantânea. Por isso, streaming é sempre um compromisso entre **velocidade e consistência**.

Esse caminho inteiro: é um pipeline

```txt
câmera → codificador → protocolo → servidor → player → decodificador → tela
```

Se qualquer ponto desse pipeline falha ou congestiona, o vídeo trava, perde quadro, atrasa ou dessincroniza do áudio. E tudo isso precisa acontecer em tempo real, o que torna live streaming muito diferente de simplesmente “enviar um arquivo”.

O mais fascinante é que, do ponto de vista teórico, transmissão ao vivo é um problema de **multiplexação temporal e controle de fluxo**. O sistema precisa garantir que o emissor não envie mais dados do que o receptor consegue consumir (controle de congestionamento), e isso envolve conceitos profundos de teoria da informação, sistemas distribuídos e redes.

E quando você pensa no streaming massivo, como YouTube, Twitch ou lives em igrejas, conferências e eventos, aí entra a **escala**. O servidor não transmite diretamente para cada espectador; ele replica o fluxo em **CDNs** (Content Delivery Networks), que são servidores geograficamente distribuídos que reduzem distância, latência e carga. A transmissão deixa de ser ponto-a-ponto e se torna um **sistema de distribuição global sincronizada**, baseado em cache, redirecionamento e balanceamento.

Ou seja, por trás de algo simples como “assistir uma live”, existe um conjunto de decisões arquiteturais, matemáticas e científicas extremamente complexas. Streaming é, no fundo, **engenharia de tempo real aplicada à comunicação digital**, lidando com a fluidez do tempo, instabilidades da rede e fragilidade da informação.

Portanto há sempre um fluxo: **OBS Studio → ProPresenter → Telões** se conectam na prática, incluindo NDI, sincronização, pacotes multicast e ajustes de jitter.

# 📺 Live Streaming - Online realtime
No nível de engenharia, de forma mais formal e técnica, não no nível de conceito pedagógico. O pipeline conceitual, onde entram os protocolos, os buffers, as camadas, e por que a transmissão ao vivo é fundamentalmente um **problema de sistemas distribuídos + controle de fluxo + compressão temporal adaptativa**.

No contexto técnico, Live Streaming é um **sistema distribuído de transmissão contínua**, definido como:

[
S = (C, E, P, D, R)
]

Onde:

* **C** = Captura (sinal bruto)
* **E** = Encoding (compressão + quantização)
* **P** = Protocolos de transporte e encapsulamento
* **D** = Distribuição (servidor ou CDN)
* **R** = Renderização (decodificação + sincronização A/V)

Esse pipeline é **streaming-oriented**, ou seja, funciona sobre buffers de tempo, não buffers de tamanho fixo.

**1. Captura**: A câmera ou dispositivo envia um stream **RAW** tipicamente YUV 4:2:0 ou 4:4:4.

Tamanhos típicos:

```
1080p RAW, 4:4:4, 30fps = ~3.19 Gbps
```

Isso é impraticável para rede. Portanto, entra:

---

**2. Encoding (Codec)**: A compressão remove redundância **espacial** e **temporal**.

Um codec como **H.264** usa:

* Transformada (DCT)
* Quantização (perda controlada)
* Predição intra-frame (intraframe)
* Predição inter-frame (motion vectors, macroblocks)
* Entropy coding (CABAC/CAVLC)

A sequência gerada é estruturada em GOPs:

```
I-frame (keyframe)
P-frames (predição para frente)
B-frames (predição bidirecional)
```

Isso **impacta a latência diretamente**:

* Menos B-frames → transmissão mais ao vivo → menor latência
* Mais B-frames → melhor qualidade por bit → aumenta atraso

Por isso **stream ao vivo** geralmente usa:

```
GOP de 1 a 2 segundos
Poucos B-frames ou nenhum
```

**3. Transporte (Protocol Layer)**: Aqui está o coração da transmissão ao vivo.

| Protocolo     | Finalidade                          | Latência    | Observações                            |
| ------------- | ----------------------------------- | ----------- | -------------------------------------- |
| **RTMP**      | Ingestão → servidor                 | Baixa       | TCP, sessão persistente                |
| **SRT**       | Ingestão de alta confiabilidade     | Baixa       | ARQ + FEC adaptativo                   |
| **RTP/RTSP**  | Broadcast corporativo               | Muito baixa | UDP, multicast possível                |
| **HLS**       | Delivery global via CDN             | Alta        | Segmentação em .ts                     |
| **MPEG-DASH** | Delivery adaptativo                 | Alta        | Similar ao HLS, independente da Apple  |
| **NDI**       | Rede local sem compressão agressiva | Muito baixa | Ideal para switcher, ProPresenter, OBS |

No seu caso (OBS → ProPresenter), **NDI** é frequentemente a ligação:

```
NDI = Vídeo + Áudio + Metadata encapsulados em fluxos UDP multicast
```

Isso permite o envio entre PCs na mesma LAN **sem precisar de servidor intermediário**.

**4. Buffering e Jitter Control**: Um player nunca reproduz o stream no momento em que chega.

Ele armazena:

[
B(t) = T_{recv} - T_{play}
]

Se o buffer cai para zero → travamento.
Se o buffer aumenta demais → atraso perceptível.

Live Streaming ajusta isso dinamicamente:

[
B'(t) = f(Jitter, Packet\ Loss, Bandwidth)
]

Onde **Jitter** = variação no tempo de chegada de pacotes.

**5. Distribuição (CDN Layer)**: Em escala global, não existe transmissão direta emissor→usuário.

Você tem **árvores de distribuição**:

```
Encoder → Origin Server → CDN Edges → Players
```

E o protocolo aqui é geralmente **HTTP chunked**, porque HTTP escala, UDP puro não.

Quando falamos de igreja, conferência ou evento local, NDI ou SDI fazem:

```
Captura → Switch → ProPresenter → Projetores/Telões
```

Sem CDN.

**6. Decodificação + Sincronização A/V**: O player reconstrói o fluxo com:

* Decodificação inversa (IDCT)
* Reordenação de frames baseada no GOP
* Ajuste de clock de áudio/vídeo via PLL e timestamps PTS/DTS

Se o clock de áudio não for referência, o vídeo perde sincronismo.

🔛 Live streaming não é “enviar vídeo”. É manter a **estabilidade temporal** de um sistema não determinístico (a rede), compensando:

* Jitter variável
* Congestionamento
* Perda de pacotes
* Diferenças de clock

Enquanto mantém:

* Largura de banda mínima estável
* Sincronização A/V
* Buffer dentro de janela operacional

Isso é **sistemas distribuídos + codificação + controle adaptativo de fluxo**.

Nível ainda mais profundo:

1. **NDI x SDI x HDMI em termos de clock domain**
2. **Como calcular bitrate ideal baseado em QP e GOP**
3. **Como reduzir latência no OBS maximizando qualidade**
4. **Como montar pipeline corporativo com SRT + HLS Low-Latency**

- Broadcast
- Multicast
- Unicast

# ⏯️ VoD - Video On Demand
