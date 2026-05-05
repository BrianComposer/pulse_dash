# Pulse Dash

**Pulse Dash** es un videojuego arcade inspirado en la lógica de *Geometry Dash*, programado en **Python + Pygame** con una arquitectura modular lista para GitHub. El proyecto está preparado para instalarse como paquete independiente y ejecutarse desde consola mediante el comando `pulse-dash`.

El juego incluye menú principal, bucle de juego, salto con física arcade, obstáculos, plataformas, monedas, sistema de vidas, puntuación, progreso de nivel, pantalla de pausa, pantalla de derrota/victoria, efectos visuales, partículas, música chiptune de 8 bits y efectos sonoros generados por código para evitar dependencias externas.

## Captura funcional esperada

El jugador controla un cubo que avanza automáticamente por un nivel lateral. Debe saltar para evitar pinchos generados dinámicamente, recoger monedas y encadenar tantos stages como puedas del nivel. Ahora dispone de varias vidas, de modo que pincharse no termina la partida inmediatamente. La partida empieza con una fase muy sencilla y la frecuencia de obstáculos aumenta progresivamente con el tiempo. La estética usa colores neón, fondo parallax, partículas y efectos de pulso.

## Instalación rápida

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate      # Windows PowerShell
pip install -e .
pulse-dash
```

También puedes instalar solo las dependencias y ejecutarlo como módulo:

```bash
pip install -r requirements.txt
python -m pulse_dash
```

## Controles

| Acción | Tecla |
|---|---|
| Saltar | Espacio / Flecha arriba / W. El salto incorpora lectura de tecla mantenida, *jump buffer* y *coyote time* para una respuesta más fluida. |
| Pausa | P / Escape |
| Reiniciar tras perder | R |
| Confirmar / empezar | Enter / Espacio |
| Salir | Escape desde el menú |

## Estructura del proyecto

```text
pulse-dash/
├── pyproject.toml
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   └── pulse_dash/
│       ├── __init__.py
│       ├── __main__.py
│       ├── main.py
│       ├── assets/
│       │   ├── images/
│       │   │   └── README.md
│       │   └── sounds/
│       │       └── README.md
│       ├── core/
│       │   ├── assets.py
│       │   ├── audio.py
│       │   ├── camera.py
│       │   ├── colors.py
│       │   ├── config.py
│       │   ├── difficulty.py
│       │   ├── game.py
│       │   ├── input.py
│       │   ├── particles.py
│       │   └── utils.py
│       ├── entities/
│       │   ├── base.py
│       │   ├── coin.py
│       │   ├── obstacle.py
│       │   ├── platform.py
│       │   └── player.py
│       ├── levels/
│       │   ├── __init__.py
│       │   ├── level_loader.py
│       │   └── level_01.json
│       └── states/
│           ├── base_state.py
│           ├── game_over.py
│           ├── menu.py
│           └── playing.py
└── tests/
    ├── difficulty_curve_test.py
    ├── input_feel_test.py
    ├── lives_and_audio_test.py
    └── smoke_test.py
```

## Desarrollo

Para ejecutar las comprobaciones principales:

```bash
python -m compileall -q src tests
python tests/input_feel_test.py
python tests/difficulty_curve_test.py
python tests/lives_and_audio_test.py
python tests/smoke_test.py
```

El test de arranque usa el driver de vídeo `dummy` de SDL para comprobar que el juego puede inicializarse en entornos sin ventana gráfica, como CI o servidores. El test de control verifica específicamente que el salto conserve pulsaciones anticipadas y permita saltar durante una breve ventana tras abandonar una plataforma. El test de dificultad comprueba que la frecuencia de obstáculos aumenta con el tiempo y que el primer obstáculo aparece a una distancia segura. El test de vidas y audio verifica que el primer impacto no causa derrota inmediata y que la música/efectos sonoros pueden inicializarse de forma segura incluso en modo headless.

## Personalización

Puedes modificar el nivel en `src/pulse_dash/levels/level_01.json`. Las coordenadas están en píxeles de mundo. En esta revisión los pinchos ya no se colocan manualmente en el JSON: los genera `core/difficulty.py` durante la partida para que la frecuencia dependa del tiempo de juego. El JSON queda reservado principalmente para longitud del nivel, plataformas, spawn y monedas.

Ejemplo de plataforma:

```json
{"type": "platform", "x": 1350, "y": 410, "w": 180, "h": 24}
```

## Notas técnicas

El diseño separa responsabilidades en módulos: estado de juego, entidades, carga de niveles, cámara, partículas, configuración y generación de assets. No requiere imágenes externas para arrancar, aunque deja carpetas listas para sustituir sprites procedurales por assets propios.

La respuesta del salto está ajustada en `core/config.py` mediante `jump_buffer_time`, `hold_jump_buffer_time`, `coyote_time`, `jump_velocity`, `gravity` y `max_fall_speed`. El sistema de vidas se ajusta con `start_lives`, `damage_invulnerability_time` y `damage_bounce_velocity`. La música y los efectos se generan en `core/audio.py`, con volumen y tempo configurables mediante `music_volume`, `sfx_volume`, `music_bpm_start` y `music_bpm_end`. La curva de dificultad también se afina desde `core/config.py`: `difficulty_warmup_seconds`, `difficulty_ramp_seconds`, `obstacle_spawn_interval_start`, `obstacle_spawn_interval_end`, `obstacle_gap_start`, `obstacle_gap_end`, `obstacle_spawn_ahead_px` y `obstacle_min_safe_ahead_px`.

## Licencia

MIT.


## Novedades rev4: stages infinitos

El juego ya no termina al superar un único nivel. Cada vez que atraviesas la puerta `NEXT`, se genera un nuevo stage procedural con una dificultad ligeramente superior. La partida conserva puntuación, monedas acumuladas y vidas restantes, y solo termina cuando pierdes todas las vidas.

La generación infinita está centralizada en:

```text
src/pulse_dash/core/stages.py
```

Los parámetros principales están en `src/pulse_dash/core/config.py`:

```python
stage_base_length
stage_length_growth
stage_max_length
stage_difficulty_step
stage_max_difficulty_bonus
stage_base_coins
stage_max_coins
stage_base_extra_platforms
stage_max_extra_platforms
```

La dificultad de obstáculos combina dos componentes: el tiempo transcurrido dentro del stage y el número de stage alcanzado. Así, cada stage empieza con un pequeño margen jugable, pero el punto de partida de la curva es cada vez más exigente.

Nuevo test incluido:

```bash
python tests/infinite_stages_test.py
```
