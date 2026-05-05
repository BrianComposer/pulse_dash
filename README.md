# Pulse Dash

**Pulse Dash** es un videojuego arcade inspirado en la lógica de *Geometry Dash*, programado en **Python + Pygame** con una arquitectura modular lista para GitHub. El proyecto está preparado para instalarse como paquete independiente y ejecutarse desde consola mediante el comando `pulse-dash`.

El juego incluye menú principal, bucle de juego, salto con física arcade, obstáculos, plataformas, monedas, puntuación, progreso de nivel, pantalla de pausa, pantalla de derrota/victoria, efectos visuales, partículas y assets generados por código para evitar dependencias externas.

## Captura funcional esperada

El jugador controla un cubo que avanza automáticamente por un nivel lateral. Debe saltar para evitar pinchos y huecos, recoger monedas y llegar al final del nivel. La estética usa colores neón, fondo parallax, partículas y efectos de pulso.

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
| Saltar | Espacio / Flecha arriba / W |
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
│       │   ├── camera.py
│       │   ├── colors.py
│       │   ├── config.py
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
    └── smoke_test.py
```

## Desarrollo

Para ejecutar el test mínimo:

```bash
python tests/smoke_test.py
```

El test usa el driver de vídeo `dummy` de SDL para comprobar que el juego puede inicializarse en entornos sin ventana gráfica, como CI o servidores.

## Personalización

Puedes modificar el nivel en `src/pulse_dash/levels/level_01.json`. Las coordenadas están en píxeles de mundo. El jugador avanza automáticamente, así que los obstáculos deben colocarse a distancias jugables.

Ejemplo de pincho:

```json
{"type": "spike", "x": 950, "y": 474, "w": 44, "h": 46}
```

Ejemplo de plataforma:

```json
{"type": "platform", "x": 1350, "y": 410, "w": 180, "h": 24}
```

## Notas técnicas

El diseño separa responsabilidades en módulos: estado de juego, entidades, carga de niveles, cámara, partículas, configuración y generación de assets. No requiere imágenes externas para arrancar, aunque deja carpetas listas para sustituir sprites procedurales por assets propios.

## Licencia

MIT.
