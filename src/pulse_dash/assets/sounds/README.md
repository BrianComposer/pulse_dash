# Sounds

Pulse Dash no necesita archivos de audio externos para arrancar. La música chiptune de 8 bits y los efectos de salto, moneda, daño y victoria se generan proceduralmente en `src/pulse_dash/core/audio.py` mediante ondas simples compatibles con `pygame.mixer`.

Puedes sustituir o ampliar esta capa más adelante añadiendo WAV/OGG a esta carpeta y cargándolos desde un `AssetStore`, pero la versión base queda completamente autocontenida para GitHub y CI.
