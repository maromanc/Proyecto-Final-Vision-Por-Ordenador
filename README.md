# Proyecto Final – Visión por Ordenador I  
## Sistema de monitorización del uso del teléfono móvil durante sesiones de estudio

Este proyecto implementa un sistema de visión por ordenador basado en técnicas clásicas de procesado de imagen, utilizando una cámara como fuente de adquisición de datos. El sistema combina un mecanismo de seguridad basado en patrones visuales con un módulo de seguimiento de objetos en tiempo real.

El sistema propuesto se ha diseñado con el objetivo de monitorizar el uso del teléfono móvil durante sesiones de estudio, permitiendo contabilizar el número de veces que el dispositivo aparece y desaparece de la escena como una medida aproximada de las interrupciones producidas durante el estudio.

---

## Objetivo del sistema

Los objetivos principales del proyecto son:
- Desarrollar un sistema de visión por ordenador que funcione en tiempo real.
- Implementar un sistema de seguridad basado en la detección y validación de una secuencia de patrones geométricos.
- Realizar el seguimiento de un teléfono móvil mediante un tracker de objeto.
- Contabilizar el número de veces que el dispositivo es utilizado durante una sesión de estudio.
- Mostrar la salida de vídeo junto con información relevante del sistema, como la tasa de refresco (FPS).

---

## Arquitectura del sistema

El sistema se estructura en varios módulos funcionales. En primer lugar, se realiza la adquisición continua de imágenes desde la cámara. A continuación, se aplica una corrección de distorsión utilizando los parámetros obtenidos en una fase de calibración offline.

Las imágenes corregidas se procesan en un sistema de seguridad encargado de detectar patrones geométricos y validar una secuencia predefinida. Mientras la secuencia no es correcta, el sistema permanece bloqueado. Una vez validada la secuencia, se activa el sistema propuesto, que realiza el seguimiento del teléfono móvil en tiempo real y contabiliza su uso. La salida del sistema se muestra de forma continua mediante una ventana de vídeo.

---

## Estructura del repositorio
├── Main.py # Sistema principal
├── secuencia_funciones.py # Sistema de seguridad (patrones y secuencia)
├── deteccion_funciones.py # Tracker del teléfono móvil
├── calibrate_camara.py # Calibración de la cámara (offline)
├── calibration_data.npz # Parámetros de calibración
├── calibration.yaml # Parámetros de calibración
├── calibration_images/ # Imágenes del patrón de calibración
|__ guardar_transformaciones.py # Para poder guardas las imágenes de la presentación
└── README.md # Documentación del proyecto


## Requisitos del sistema

Para la correcta ejecución del proyecto es necesario disponer de Python 3.10 y de las librerías OpenCV y NumPy.

## Ejecución del proyecto

Antes de ejecutar el sistema principal es necesario realizar la calibración de la cámara. Este proceso se ejecuta una única vez y genera los ficheros que contienen los parámetros de calibración. se hace ejecutando python calibrate_camara.py

Una vez realizada la calibración, el sistema principal puede ejecutarse mediante el siguiente comando: python Main.py

Durante la ejecución, el sistema mostrará la salida de vídeo en tiempo real.

## Funcionamiento del sistema

El sistema funciona en dos fases diferenciadas. En la primera fase, el sistema opera en modo de seguridad, en el que el usuario debe introducir correctamente una secuencia predefinida de patrones geométricos para desbloquear el sistema. Mientras la secuencia no sea correcta, el sistema permanece bloqueado y únicamente se muestra la información correspondiente a la detección de patrones. En la segunda fase, una vez validada la secuencia, se activa el sistema de seguimiento del teléfono móvil. El tracker mantiene una bounding box alrededor del dispositivo y contabiliza las veces que este aparece y desaparece de la escena, proporcionando una medida aproximada del uso del móvil durante la sesión de estudio. La salida del sistema se muestra de forma continua, incluyendo la tasa de refresco (FPS).

## Resultados esperados

El sistema permite monitorizar de forma visual y cuantitativa el uso del teléfono móvil durante sesiones de estudio, ejecutándose de manera fluida y estable en tiempo real. El diseño modular facilita la comprensión del sistema y su posible ampliación a otros escenarios de análisis visual.

## Autoría y uso de IA

Proyecto desarrollado como parte del Proyecto Final de la asignatura Visión por Ordenador I. Se ha utilizado un asistente de inteligencia artificial como apoyo para la estructuración del código y la redacción de la documentación, bajo supervisión y validación del autor.
