# Instrucciones para correr el desarrollo y los tests por línea de comando


# Decisiones de diseño

Decidimos encarar el desarrollo separando el problema en dos partes:
- Un módulo que se encargue de las estrategias de validación según medio de pago (patrón strategy)
- Otro módulo independiente que incluya la lógica y el flujo de estados del sistema de pagos (patrón state)

Luego un orquestador gestiona los pagos consumiendo desde ambos módulos

Una aclaración a tener en cuenta: en models.py, que es el archivo que maneja los estados, definimos constantes que también se usan en validation_strategy.py. Esto lo hicimos así porque en un principio empezamos cada uno definiendo las constantes cada uno por separado pero nos parecio más consistente unificar el criterio. Sabemos que la mejor practica sería manejar eso en un archivo separado desde el cuál cada módulo pueda importar esa lógica, pero en este caso nos quedó dentro de models.py... es una optimización que va a quedar pendiente.

También creamos test de validación para cada módulo en la carpeta tests, que automatizamos con CI en el repositorio para asegurar de no romper nada al hacer los pull request de cada funcionalidad.

Finalmente dejamos funcionando en una API el orquestador principal que gestiona los pagos, main.py

La estructura del repo quedó un poco desordenada quizas: la parte de validación para cada medio de pago (validation_strategy.py) se encuentra en la carpeta /strategies, mientras que la lógica de estados quedo en models.py en la raiz del repositorio
