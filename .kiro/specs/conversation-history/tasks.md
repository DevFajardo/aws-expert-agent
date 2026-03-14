# Plan de Implementación: Conversation History

## Overview

Implementar el módulo `history_manager.py` con la clase `HistoryManager` e integrarla en `agent.py` para persistir el historial de conversación en `historial.json`.

## Tasks

- [ ] 1. Crear el módulo `history_manager.py` con la clase `HistoryManager`
  - Definir la clase con `__init__`, `load`, `save_entry` y `summary`
  - `load()` lee `historial.json`; retorna `[]` si no existe o el JSON es inválido, imprimiendo advertencia en este último caso
  - `save_entry()` añade la entrada al historial en memoria y escribe el arreglo completo de forma atómica usando `tempfile.NamedTemporaryFile` + `os.replace()`; ante error de escritura imprime advertencia y continúa
  - `summary()` retorna string con número de entradas y timestamp de la más reciente, o mensaje de "sin historial previo" si la lista está vacía
  - Cada `ConversationEntry` incluye los campos `timestamp` (ISO 8601), `pregunta` y `respuesta`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 4.1, 4.2_

  - [ ]* 1.1 Escribir tests unitarios para `HistoryManager`
    - `load()` con archivo inexistente → retorna `[]`
    - `load()` con JSON inválido → retorna `[]` y emite warning
    - `load()` con arreglo válido → retorna la lista correcta
    - `summary()` con lista vacía → mensaje "sin historial previo"
    - `summary()` con N entradas → contiene N y el timestamp correcto
    - `save_entry()` crea el archivo si no existe
    - `save_entry()` con error de escritura → no lanza excepción
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 4.1, 4.2_

  - [ ]* 1.2 Escribir property test — Property 1: Round-trip de guardado
    - **Property 1: Round-trip de guardado**
    - Para cualquier par (pregunta, respuesta), tras `save_entry()` el archivo debe ser JSON válido, lista, y el último elemento contiene los campos correctos con timestamp ISO 8601
    - **Validates: Requirements 1.1, 1.4**

  - [ ]* 1.3 Escribir property test — Property 2: Append sin pérdida de entradas
    - **Property 2: Append sin pérdida de entradas**
    - Para cualquier secuencia de N pares guardados uno a uno, el arreglo resultante tiene exactamente N elementos en el mismo orden
    - **Validates: Requirements 1.2**

  - [ ]* 1.4 Escribir property test — Property 3: Robustez de carga
    - **Property 3: Robustez de carga**
    - Para cualquier estado del archivo (inexistente, vacío, JSON inválido), `load()` retorna `[]` sin lanzar excepción
    - **Validates: Requirements 2.2, 2.3**

  - [ ]* 1.5 Escribir property test — Property 4: Resumen de historial no vacío
    - **Property 4: Resumen de historial no vacío**
    - Para cualquier lista con al menos un elemento, `summary()` retorna string con el número total de entradas y el timestamp de la más reciente
    - **Validates: Requirements 3.1**

  - [ ]* 1.6 Escribir property test — Property 5: Resiliencia ante errores de escritura
    - **Property 5: Resiliencia ante errores de escritura**
    - Ante cualquier condición que cause error de escritura, `save_entry()` no lanza excepción y emite advertencia
    - **Validates: Requirements 4.1**

- [ ] 2. Checkpoint — Asegurar que todos los tests pasan
  - Asegurar que todos los tests pasan, consultar al usuario si surgen dudas.

- [ ] 3. Integrar `HistoryManager` en `agent.py`
  - Importar `HistoryManager` desde `history_manager`
  - Instanciar `HistoryManager` antes del loop en `main()`
  - Llamar `history_manager.load()` al inicio de `main()`
  - Imprimir `history_manager.summary()` antes del primer prompt al usuario
  - Llamar `history_manager.save_entry(user_input, str(response))` tras cada respuesta del agente
  - _Requirements: 2.1, 3.1, 3.2, 3.3, 1.1_

  - [ ]* 3.1 Escribir test de integración para el flujo completo en `agent.py`
    - Verificar que el resumen se muestra antes del primer prompt
    - Verificar que `save_entry` se invoca tras cada respuesta
    - _Requirements: 3.3, 1.1_

- [ ] 4. Checkpoint final — Asegurar que todos los tests pasan
  - Asegurar que todos los tests pasan, consultar al usuario si surgen dudas.

## Notes

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido
- Cada tarea referencia los requisitos específicos para trazabilidad
- Los property tests usan **Hypothesis** (`pip install hypothesis`)
- La escritura atómica garantiza que `historial.json` nunca queda en estado parcial
