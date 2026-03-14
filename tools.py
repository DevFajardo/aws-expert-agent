from strands import tool


@tool
def estimar_costo_lambda(
    invocaciones: int,
    duracion_ms: float,
    memoria_mb: int,
) -> str:
    """
    Calcula el costo mensual estimado de AWS Lambda.

    Usa los precios estándar de AWS Lambda:
    - Costo por solicitud: $0.20 por millón de invocaciones
    - Costo por duración: $0.0000166667 por GB-segundo

    Args:
        invocaciones: Número total de invocaciones al mes.
        duracion_ms: Duración promedio de cada invocación en milisegundos.
        memoria_mb: Memoria asignada a la función en MB.

    Returns:
        Resumen del costo mensual estimado en USD.
    """
    precio_por_millon_requests = 0.20
    precio_por_gb_segundo = 0.0000166667
    requests_gratuitas = 1_000_000
    gb_segundos_gratuitos = 400_000

    costo_requests = max(0, invocaciones - requests_gratuitas) / 1_000_000 * precio_por_millon_requests

    duracion_segundos = duracion_ms / 1000
    gb_segundos = (memoria_mb / 1024) * duracion_segundos * invocaciones
    costo_duracion = max(0, gb_segundos - gb_segundos_gratuitos) * precio_por_gb_segundo

    costo_total = costo_requests + costo_duracion

    return (
        f"Estimación mensual AWS Lambda:\n"
        f"  - Invocaciones:      {invocaciones:,}\n"
        f"  - Duración promedio: {duracion_ms} ms\n"
        f"  - Memoria:           {memoria_mb} MB\n"
        f"  - GB-segundos:       {gb_segundos:,.2f}\n"
        f"  - Costo requests:    ${costo_requests:.4f}\n"
        f"  - Costo duración:    ${costo_duracion:.4f}\n"
        f"  - TOTAL ESTIMADO:    ${costo_total:.4f} USD/mes\n"
        f"  (Incluye capa gratuita: 1M requests y 400K GB-s)"
    )


@tool
def recomendar_arquitectura(caso_de_uso: str) -> str:
    """
    Devuelve una arquitectura AWS recomendada según el caso de uso.

    Args:
        caso_de_uso: Tipo de aplicación a construir. Valores soportados:
                     'api_rest', 'streaming', 'ml_inference', 'static_web', 'batch'.

    Returns:
        Descripción de la arquitectura recomendada con los servicios AWS involucrados.
    """
    arquitecturas: dict[str, dict] = {
        "api_rest": {
            "titulo": "API REST Serverless",
            "servicios": ["Amazon API Gateway", "AWS Lambda", "Amazon DynamoDB", "AWS IAM", "Amazon CloudWatch"],
            "descripcion": "Arquitectura serverless ideal para APIs con tráfico variable. API Gateway maneja las rutas HTTP, Lambda ejecuta la lógica de negocio y DynamoDB provee persistencia de baja latencia.",
            "patron": "API Gateway → Lambda → DynamoDB",
        },
        "streaming": {
            "titulo": "Procesamiento de Streaming en Tiempo Real",
            "servicios": ["Amazon Kinesis Data Streams", "AWS Lambda", "Amazon S3", "Amazon OpenSearch Service", "Amazon CloudWatch"],
            "descripcion": "Pipeline para ingestión y procesamiento de eventos en tiempo real. Kinesis captura el stream, Lambda procesa cada batch y los resultados se almacenan en S3 u OpenSearch para análisis.",
            "patron": "Kinesis → Lambda → S3 / OpenSearch",
        },
        "ml_inference": {
            "titulo": "Inferencia de Machine Learning",
            "servicios": ["Amazon SageMaker Endpoints", "AWS Lambda", "Amazon API Gateway", "Amazon S3", "Amazon ECR"],
            "descripcion": "Arquitectura para servir modelos ML en producción. SageMaker gestiona el endpoint del modelo con auto-scaling, Lambda orquesta pre/post-procesamiento y API Gateway expone el servicio.",
            "patron": "API Gateway → Lambda → SageMaker Endpoint",
        },
        "static_web": {
            "titulo": "Sitio Web Estático con CDN Global",
            "servicios": ["Amazon S3", "Amazon CloudFront", "AWS Certificate Manager", "Amazon Route 53", "AWS WAF"],
            "descripcion": "Hosting de alta disponibilidad para SPAs y sitios estáticos. S3 almacena los assets, CloudFront los distribuye globalmente con baja latencia, Route 53 gestiona el DNS y WAF protege contra ataques.",
            "patron": "Route 53 → CloudFront → S3",
        },
        "batch": {
            "titulo": "Procesamiento Batch",
            "servicios": ["AWS Batch", "Amazon S3", "AWS Step Functions", "Amazon SQS", "Amazon CloudWatch"],
            "descripcion": "Orquestación de trabajos batch de gran escala. Step Functions coordina el flujo, SQS desacopla la carga, AWS Batch gestiona los workers con EC2/Fargate y S3 almacena inputs/outputs.",
            "patron": "S3 / SQS → Step Functions → AWS Batch → S3",
        },
    }

    caso = caso_de_uso.lower().strip()
    if caso not in arquitecturas:
        disponibles = ", ".join(arquitecturas.keys())
        return f"Caso de uso '{caso_de_uso}' no reconocido. Opciones disponibles: {disponibles}"

    arq = arquitecturas[caso]
    servicios_str = "\n".join(f"    • {s}" for s in arq["servicios"])

    return (
        f"Arquitectura recomendada: {arq['titulo']}\n\n"
        f"Patrón: {arq['patron']}\n\n"
        f"Servicios involucrados:\n{servicios_str}\n\n"
        f"Descripción: {arq['descripcion']}"
    )


@tool
def buscar_servicio_aws(categoria: str) -> str:
    """
    Lista los principales servicios AWS disponibles en una categoría.

    Args:
        categoria: Categoría de servicios a consultar. Valores soportados:
                   'compute', 'storage', 'database', 'ai', 'networking'.

    Returns:
        Lista de servicios AWS de la categoría con una breve descripción de cada uno.
    """
    catalogo: dict[str, list[dict]] = {
        "compute": [
            {"nombre": "Amazon EC2", "descripcion": "Máquinas virtuales escalables en la nube"},
            {"nombre": "AWS Lambda", "descripcion": "Ejecución de código serverless sin gestionar servidores"},
            {"nombre": "Amazon ECS", "descripcion": "Orquestación de contenedores Docker administrada"},
            {"nombre": "Amazon EKS", "descripcion": "Kubernetes administrado en AWS"},
            {"nombre": "AWS Fargate", "descripcion": "Cómputo serverless para contenedores (ECS/EKS)"},
            {"nombre": "AWS Batch", "descripcion": "Procesamiento batch administrado a escala"},
        ],
        "storage": [
            {"nombre": "Amazon S3", "descripcion": "Almacenamiento de objetos escalable y duradero"},
            {"nombre": "Amazon EBS", "descripcion": "Volúmenes de bloque de alto rendimiento para EC2"},
            {"nombre": "Amazon EFS", "descripcion": "Sistema de archivos NFS administrado y elástico"},
            {"nombre": "AWS Glacier", "descripcion": "Archivado de datos de bajo costo a largo plazo"},
            {"nombre": "AWS Storage Gateway", "descripcion": "Integración híbrida entre on-premise y S3"},
        ],
        "database": [
            {"nombre": "Amazon RDS", "descripcion": "Bases de datos relacionales administradas (MySQL, PostgreSQL, etc.)"},
            {"nombre": "Amazon Aurora", "descripcion": "Base de datos relacional compatible con MySQL/PostgreSQL de alto rendimiento"},
            {"nombre": "Amazon DynamoDB", "descripcion": "Base de datos NoSQL serverless de baja latencia"},
            {"nombre": "Amazon ElastiCache", "descripcion": "Caché en memoria con Redis o Memcached"},
            {"nombre": "Amazon Redshift", "descripcion": "Data warehouse columnar para analítica a escala"},
            {"nombre": "Amazon Neptune", "descripcion": "Base de datos de grafos administrada"},
        ],
        "ai": [
            {"nombre": "Amazon Bedrock", "descripcion": "Acceso a modelos fundacionales (LLMs) vía API"},
            {"nombre": "Amazon SageMaker", "descripcion": "Plataforma completa para entrenar y desplegar modelos ML"},
            {"nombre": "Amazon Rekognition", "descripcion": "Análisis de imágenes y video con visión artificial"},
            {"nombre": "Amazon Textract", "descripcion": "Extracción de texto y datos de documentos"},
            {"nombre": "Amazon Comprehend", "descripcion": "Procesamiento de lenguaje natural (NLP)"},
            {"nombre": "Amazon Polly", "descripcion": "Conversión de texto a voz realista"},
            {"nombre": "Amazon Transcribe", "descripcion": "Transcripción automática de audio a texto"},
        ],
        "networking": [
            {"nombre": "Amazon VPC", "descripcion": "Red privada virtual aislada en la nube"},
            {"nombre": "Amazon CloudFront", "descripcion": "CDN global para distribución de contenido con baja latencia"},
            {"nombre": "Amazon Route 53", "descripcion": "Servicio DNS escalable y de alta disponibilidad"},
            {"nombre": "AWS Direct Connect", "descripcion": "Conexión dedicada entre on-premise y AWS"},
            {"nombre": "AWS Transit Gateway", "descripcion": "Hub central para interconectar VPCs y redes on-premise"},
            {"nombre": "Elastic Load Balancing", "descripcion": "Distribución automática de tráfico entre instancias"},
        ],
    }

    cat = categoria.lower().strip()
    if cat not in catalogo:
        disponibles = ", ".join(catalogo.keys())
        return f"Categoría '{categoria}' no reconocida. Opciones disponibles: {disponibles}"

    servicios = catalogo[cat]
    lineas = "\n".join(f"  • {s['nombre']}: {s['descripcion']}" for s in servicios)

    return f"Servicios AWS — categoría '{cat}':\n\n{lineas}"
