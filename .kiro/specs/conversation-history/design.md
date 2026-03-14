# Design Document: Conversation History

## Overview

Se agrega al agente AWS Expert la capacidad de persistir el historial de conversación en un archivo JSON (`historial.json`). El componente `HistoryManager` encapsula toda la lógica de lectura, escritura y resumen del historial, manteniéndola separada de la lógica del agente en `agent.py`.

El flujo general es:
1. Al iniciar, `HistoryManager` carga `historial.json` (o inicializa lista vacía si no existe / JSON inválido).
2. El agente muestra un resumen del historial cargado antes de la primera interacción.
3. Tras cada intercambio usuario-agente, `HistoryManager` persiste la nueva entrada de forma atómica.
4. Errores de escritura se reportan como advertencias sin interrumpir la sesión.

## Architecture

```mermaid
flowchart TD
    A[agent.py - main()] --> B[HistoryManager.load()]
    B --> C{historial.json existe?}
    C -- No --> D[lista vacía]
    C -- Sí, JSON válido --> E[lista de entradas]
    C -- Sí, JSON inválido --> F[lista vacía + warning]
    D & E & F --> G[mostrar resumen en consola]
    G --> H[loop de conversación]
    H --> I[usuario envía pregunta]
    I --> J[agent(user_input)]
    J --> K[HistoryManager.save_entry(pregunta, respuesta)]
    K --> L{escritura atómica OK?}
    L -- Sí --> H
    L -- No --> M[warning en consola] --> H
```

La nueva clase `HistoryManager` se implementa en un módulo separado `history_manager.py`. `agent.py` la instancia y la usa en el loop principal.

## Components and Interfaces

### HistoryManager (`history_manager.py`)

```python
class HistoryManager:
    def __init__(self, filepath: str = "historial.json") -> None: ...

    def load(self) -> list[dict]:
        """
        Lee historial.json y retorna la lista de entradas.
        Si el archivo no existe, retorna [].
        Si el JSON es inválido, imprime advertencia y retorna [].
        """

    def save_entry(self, pregunta: str, respuesta: str) -> None:
        """
        Añade una ConversationEntry al historial en memoria y persiste
        el arreglo completo en historial.json de forma atómica.
        Si ocurre un error de escritura, imprime advertencia y continúa.
        """

    def summary(self) -> str:
        """
        Retorna un string con el resumen del historial:
        - Si vacío: mensaje indicando que no hay historial previo.
        - Si no vacío: número de entradas y timestamp de la más reciente.
        """
```

### Cambios en `agent.py`

- Instanciar `HistoryManager` antes del loop.
- Llamar `history_manager.load()` al inicio.
- Imprimir `history_manager.summary()` antes del primer prompt.
- Llamar `history_manager.save_entry(user_input, str(response))` tras cada respuesta.

## Data Models

### ConversationEntry

Cada entrada del historial es un objeto JSON con la siguiente estructura:

```json
{
  "timestamp": "2024-01-15T10:30:00.123456",
  "pregunta": "¿Cuánto cuesta Lambda con 1M invocaciones?",
  "respuesta": "Estimación mensual AWS Lambda: ..."
}
```

| Campo       | Tipo   | Descripción                                      |
|-------------|--------|--------------------------------------------------|
| `timestamp` | string | Fecha y hora ISO 8601 del momento del guardado   |
| `pregunta`  | string | Texto enviado por el usuario                     |
| `respuesta` | string | Texto de respuesta generado por el agente        |

### History File (`historial.json`)

Arreglo JSON de objetos `ConversationEntry`:

```json
[
  {
    "timestamp": "2024-01-15T10:30:00.123456",
    "pregunta": "...",
    "respuesta": "..."
  }
]
```

### Escritura atómica

Para evitar corrupción, la escritura usa el patrón write-to-temp-then-rename:
1. Serializar el arreglo completo a un archivo temporal en el mismo directorio.
2. Renombrar el temporal al path definitivo (`historial.json`) con `os.replace()`.

Esto garantiza que el archivo siempre contiene un JSON completo y válido.


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Round-trip de guardado

*Para cualquier* par (pregunta, respuesta) y cualquier estado previo del archivo (existente, inexistente o vacío), después de llamar a `save_entry(pregunta, respuesta)`, el archivo `historial.json` debe poder parsearse como JSON, ser una lista, y su último elemento debe contener exactamente los campos `pregunta`, `respuesta` y un `timestamp` con formato ISO 8601.

**Validates: Requirements 1.1, 1.4**

### Property 2: Append sin pérdida de entradas

*Para cualquier* secuencia de N pares (pregunta, respuesta) guardados uno a uno, el arreglo resultante en `historial.json` debe tener exactamente N elementos y todos los pares anteriores deben seguir presentes en el mismo orden.

**Validates: Requirements 1.2**

### Property 3: Robustez de carga

*Para cualquier* estado del archivo de historial — inexistente, con contenido vacío, o con contenido que no es JSON válido — `load()` debe retornar una lista vacía sin lanzar ninguna excepción.

**Validates: Requirements 2.2, 2.3**

### Property 4: Resumen de historial no vacío

*Para cualquier* lista de entradas con al menos un elemento, `summary()` debe retornar un string que contenga el número total de entradas y el timestamp de la entrada más reciente.

**Validates: Requirements 3.1**

### Property 5: Resiliencia ante errores de escritura

*Para cualquier* condición que cause un error de escritura (e.g., directorio de solo lectura), `save_entry()` no debe lanzar ninguna excepción y debe emitir un mensaje de advertencia.

**Validates: Requirements 4.1**

## Error Handling

| Situación | Comportamiento |
|-----------|---------------|
| `historial.json` no existe al cargar | `load()` retorna `[]`, sin error |
| `historial.json` contiene JSON inválido | `load()` retorna `[]`, imprime advertencia |
| Error de escritura en `save_entry()` | Imprime advertencia, continúa la sesión |
| Respuesta del agente no es string | Se convierte con `str()` antes de guardar |

La escritura atómica usa `tempfile.NamedTemporaryFile` + `os.replace()` en el mismo directorio para garantizar que el archivo nunca queda en estado parcial.

## Testing Strategy

### Unit Tests

Cubren ejemplos concretos y casos borde:

- `load()` con archivo inexistente → retorna `[]`
- `load()` con JSON inválido → retorna `[]` y emite warning
- `load()` con arreglo válido → retorna la lista correcta
- `summary()` con lista vacía → mensaje "sin historial previo"
- `summary()` con N entradas → contiene N y el timestamp correcto
- `save_entry()` crea el archivo si no existe
- `save_entry()` con error de escritura → no lanza excepción

### Property-Based Tests

Se usa **Hypothesis** (librería PBT estándar para Python). Cada test corre mínimo 100 iteraciones.

```python
# Feature: conversation-history, Property 1: Round-trip de guardado
@given(pregunta=st.text(min_size=1), respuesta=st.text())
@settings(max_examples=100)
def test_save_entry_round_trip(pregunta, respuesta): ...

# Feature: conversation-history, Property 2: Append sin pérdida de entradas
@given(entradas=st.lists(st.tuples(st.text(min_size=1), st.text()), min_size=1, max_size=20))
@settings(max_examples=100)
def test_append_preserves_previous_entries(entradas): ...

# Feature: conversation-history, Property 3: Robustez de carga
@given(contenido=st.one_of(st.just(""), st.text().filter(lambda s: not _is_valid_json(s))))
@settings(max_examples=100)
def test_load_robustness(contenido): ...

# Feature: conversation-history, Property 4: Resumen de historial no vacío
@given(entradas=st.lists(st.fixed_dictionaries({
    "timestamp": st.datetimes().map(lambda d: d.isoformat()),
    "pregunta": st.text(min_size=1),
    "respuesta": st.text()
}), min_size=1, max_size=50))
@settings(max_examples=100)
def test_summary_non_empty(entradas): ...

# Feature: conversation-history, Property 5: Resiliencia ante errores de escritura
@given(pregunta=st.text(min_size=1), respuesta=st.text())
@settings(max_examples=100)
def test_save_entry_write_error_resilience(pregunta, respuesta): ...
```

Cada property test implementa exactamente una propiedad del documento de diseño. Los unit tests complementan cubriendo ejemplos específicos e integraciones.
