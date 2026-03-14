# Requirements Document

## Introduction

Esta funcionalidad agrega al agente AWS Expert la capacidad de persistir el historial de conversación en un archivo JSON (`historial.json`). Cada interacción (pregunta del usuario + respuesta del agente) se guarda con su timestamp. Al iniciar, el agente carga el historial existente y muestra un resumen al usuario.

## Glossary

- **Agent**: El agente Python definido en `agent.py` que interactúa con el usuario vía consola.
- **History_Manager**: Componente responsable de leer, escribir y resumir el historial de conversación.
- **Conversation_Entry**: Unidad de historial que contiene timestamp, pregunta del usuario y respuesta del agente.
- **History_File**: Archivo `historial.json` ubicado en el directorio raíz del proyecto donde se persiste el historial.
- **Session**: Una ejecución continua del agente desde que inicia hasta que el usuario escribe `salir`.

## Requirements

### Requirement 1: Persistencia de entradas de conversación

**User Story:** Como usuario del agente, quiero que cada pregunta y respuesta quede guardada en un archivo JSON, para poder revisar conversaciones anteriores.

#### Acceptance Criteria

1. WHEN el usuario envía una pregunta y el agente genera una respuesta, THE History_Manager SHALL guardar una Conversation_Entry en el History_File con los campos: `timestamp` (ISO 8601), `pregunta` y `respuesta`.
2. THE History_Manager SHALL añadir cada nueva Conversation_Entry al final del arreglo existente en el History_File, sin sobrescribir entradas previas.
3. THE History_File SHALL contener un arreglo JSON válido de objetos Conversation_Entry.
4. IF el History_File no existe al momento de guardar, THEN THE History_Manager SHALL crear el History_File con la nueva Conversation_Entry como primer elemento del arreglo.

### Requirement 2: Carga del historial al iniciar

**User Story:** Como usuario del agente, quiero que al iniciar el agente se cargue el historial previo, para tener contexto de conversaciones anteriores.

#### Acceptance Criteria

1. WHEN el Agent inicia, THE History_Manager SHALL intentar leer el History_File desde el directorio raíz del proyecto.
2. IF el History_File no existe al iniciar, THEN THE History_Manager SHALL inicializar el historial como una lista vacía y continuar sin error.
3. IF el History_File existe pero contiene JSON inválido, THEN THE History_Manager SHALL inicializar el historial como una lista vacía y mostrar un mensaje de advertencia al usuario.

### Requirement 3: Resumen del historial al iniciar

**User Story:** Como usuario del agente, quiero ver un resumen del historial al iniciar, para saber cuántas conversaciones previas existen sin leer todo el archivo.

#### Acceptance Criteria

1. WHEN el Agent inicia y el historial cargado contiene al menos una Conversation_Entry, THE Agent SHALL mostrar en consola el número total de entradas previas y el timestamp de la entrada más reciente.
2. WHEN el Agent inicia y el historial está vacío, THE Agent SHALL mostrar en consola un mensaje indicando que no hay historial previo.
3. THE Agent SHALL mostrar el resumen del historial antes de solicitar la primera entrada al usuario.

### Requirement 4: Integridad del historial

**User Story:** Como usuario del agente, quiero que el historial no se corrompa ante errores durante el guardado, para no perder entradas previas.

#### Acceptance Criteria

1. IF ocurre un error de escritura al guardar una Conversation_Entry, THEN THE History_Manager SHALL mostrar un mensaje de advertencia en consola y continuar la ejecución del Agent sin interrumpir la sesión.
2. THE History_Manager SHALL escribir el History_File de forma atómica, completando la escritura completa del arreglo antes de cerrar el archivo.
