# Examen Módulo 1: API de Sistema de Pagos - Moscato y Karzovinik

API pública para gestionar pagos en línea, implementada con FastAPI y una arquitectura modular basada en Patrones de Diseño (Strategy, State). El sistema soporta el registro, pago con validación  , actualización y reversión de transacciones.

---

## Despliegue y Pruebas

### URL de la API (Render.com)

* [https://examen-modulo1.onrender.com](https://examen-modulo1.onrender.com)

### Instrucciones para Correr Localmente

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/FranMoscato/examen_modulo1.git
    cd examen_modulo1
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    # En Windows PowerShell
    .\venv\Scripts\Activate.ps1
    # En macOS/Linux
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la API:**
    ```bash
    uvicorn main:app --reload
    ```

5.  **Acceder a la API local:**
    * **Documentación:** `http://127.0.0.1:8000/docs`

### Instrucciones para Correr Tests

Para ejecutar la suite completa de tests unitarios (ambos módulos, State y Strategy), usa el comando `discover` desde la raíz del proyecto:

```bash
python -m unittest discover tests
```

## Decisiones de Diseño y Arquitectura

Para trabajar en el proyecto, decidimos separar la lógica en módulos independientes para poder trabajar en paralelo y mantener el código ordenado.

### 1. Patrones que usamos

* **Patrón Strategy:** Estructuramos esto en `strategies/validation_strategy.py` para manejar las reglas de validación de los medios de pago. Cada método de pago (`Tarjeta de Credito` y `PayPal`) es una "estrategia" distinta, con sus propias reglas de validación.
    * **¿Por qué?** Si el dia de mañana queremos agregar "Cripto" como método de pago, solo creamos una nueva clase y la agregamos al *factory*, sin tocar `main.py`.

* **Patrón State:** Se encuentra en `states/states.py` para controlar el ciclo de vida del pago (`REGISTRADO`, `PAGADO`, `FALLIDO`).
    * **¿Por qué?** El objeto `Payment` cambia su comportamiento según el estado. Por ejemplo, la acción `updatear` solo funciona si el estado es `REGISTRADO`. Esto evita tener un montón de `if/else` en `main.py`. Además, como el flujo de transición de estados no depende del medio de pago, tiene sentido trabajarlo en este módulo independiente.

### 2. Tests

* Decidimos separar los tests en `test_strategies.py` (para validar la lógica de montos y reglas) y `test_states.py` (para validar el flujo de estados).
* No probamos la escritura en `data.json` en los *tests unitarios*, solo la lógica de negocio. Las pruebas de la API local cubren esa parte de la integración.

### 3. Suposiciones

* La regla de Tarjeta de Crédito "no haya más de 1 pago REGISTRADO" la interpretamos como que no puede haber otro pago con TC en estado `REGISTRADO` en el sistema al momento de validar (el único que puede estar en estado REGISTRADO es el pago que se está procesando).
* `data.json` actúa como nuestra base de datos (basado en el código de referencia). Se carga y guarda en cada llamada a la API.

### 4. Flujo de Estados

El flujo que sigue el Patrón State es:

* **REGISTRADO** (Inicial)
    * $\rightarrow$ `Pagar` (valida OK) $\rightarrow$ **PAGADO**
    * $\rightarrow$ `Pagar` (NO valida OK) $\rightarrow$ **FALLIDO**
    * $\rightarrow$ `Updatear` (OK) $\rightarrow$ **REGISTRADO**
* **FALLIDO**
    * $\rightarrow$ `Revertir` (OK) $\rightarrow$ **REGISTRADO**
* **PAGADO**
    * (Estado final, no permite más acciones)

### 5. Otros comentarios sobre el proceso y desarrollo del trabajo

Esta sección cubre otros puntos relevantes de nuestro proceso de trabajo, las decisiones que tomamos y los problemas que fuimos resolviendo.

#### Decisiones de Arquitectura y "Refactorización"

Una decisión clave fue cómo estructurar nuestros modelos de datos.

* **Problema:** Inicialmente, nuestro archivo `models.py` mezclaba responsabilidades. Contenía tanto la lógica del **Patrón State** (las clases `REGISTRADO`, `FALLIDO`, etc.) como las constantes y, al mismo tiempo, debía soportar la validación de la API.
* **Solución:** Nos dimos cuenta de que esto no estaba del todo correcto porque `models.py` manejaba el módulo de estados y al mismo tiempo alimentaba a `validation_strategy.py` lo cual no tiene mucho sentido, creando **deuda técnica**.
Decidimos actualizar la arquitectura: movimos toda la lógica del Patrón State a su propio módulo (`states/states.py`). De esa manera `models.py` quedó limpio, conteniendo solo constantes para unificar criterios entre módulos.

#### Iteración y Corrección de Errores

El desarrollo no fue lineal. Tuvimos que iterar sobre varias soluciones:

* **Tests Unitarios:** Tuvimos un error en `test_strategies.py` donde un test fallaba porque los datos de prueba (`setUp`) interferían con otros. Lo corregimos aislando los datos de cada test.
* **Integración Continua (CI):** El CI fallaba porque no ejecutaba todos nuestros tests. Descubrimos que el comando `unittest discover` busca archivos que empiecen con `test_*.py`, y nuestro archivo `unittest_estados.py` no cumplía ese patrón. Lo renombramos a `test_states.py` y el CI pudo descubrir y correr la suite completa.

#### Colaboración y Flujo de Git

Siendo esta una de nuestras primeras prácticas colaborativas intensivas con Git, nuestro historial de *commits* y el manejo de ramas no siempre fue el más prolijo.

Sin embargo, nos enfocamos en el objetivo principal de la colaboración: usar **Pull Requests** como el punto central de integración. Intentamos que cada PR representara una unidad de trabajo funcional (ej. "implementar estrategias de validación y sus tests"), permitiendo al otro miembro revisar el código y asegurar que los *checks* automáticos de la CI pasaran antes de fusionar a `main`.

#### Uso de Herramientas de IA

Para ser transparentes, queriamos dejar aclarado que utilizamos herramientas de IA (LLMs) como asistente durante el desarrollo. Las usamos principalmente para:
* Acelerar la escritura de código.
* Ayudar a ordenar y estructurar el repositorio.
* Ayudar a depurar errores que nos fuimos encontrando (como `ImportError` por la dependencia circular).
* Sugerir estrategias de refactorización.

En todo momento, quisimos usar la IA para entender mejor y aplicar los conceptos de la materia, no para evitar el trabajo de diseño. Siempre mantuvimos el espiritu de entender el fondo de la cuestión y poner en practica lo que venimos viendo en la cursada. De hecho, una reflexión que nos llevamos es que al usar IA para ayudarse en este tipo de trabajos, en muchos momentos te complejiza más de lo que debería/podría, sugiriendo pasos, estrategias y cambios que tampoco hacían mucho sentido para poder completar este trabajo teniendo en cuenta el scope y objetivo de este. En ese sentido, creemos que pudimos mantenernos bastante criteriosos para decidir que "recomendaciones" y ayudas tomar, y cuáles dejar.