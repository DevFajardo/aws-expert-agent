from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator, current_time
from tools import buscar_servicio_aws, estimar_costo_lambda, recomendar_arquitectura

load_dotenv()

model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    region_name="us-east-1",
)

agent = Agent(
    model=model,
    tools=[
        # Herramientas custom AWS
        estimar_costo_lambda,
        recomendar_arquitectura,
        buscar_servicio_aws,
        # Herramientas built-in de Strands
        calculator,
        current_time,
    ],
    system_prompt=(
        "Eres un experto en Amazon Web Services (AWS) con amplio conocimiento en "
        "arquitectura cloud, servicios administrados, seguridad, costos y buenas prácticas. "
        "Responde siempre en español, de forma clara y concisa. "
        "Cuando sea útil, incluye ejemplos prácticos o comandos de AWS CLI.\n\n"
        "Tienes acceso a las siguientes herramientas:\n"
        "- estimar_costo_lambda: calcula el costo mensual de AWS Lambda dado número de "
        "invocaciones, duración en ms y memoria en MB.\n"
        "- recomendar_arquitectura: sugiere una arquitectura AWS según el caso de uso "
        "(api_rest, streaming, ml_inference, static_web, batch).\n"
        "- buscar_servicio_aws: lista servicios AWS por categoría "
        "(compute, storage, database, ai, networking).\n"
        "- calculator: realiza operaciones matemáticas.\n"
        "- current_time: obtiene la fecha y hora actual.\n"
        "Usa estas herramientas siempre que sean relevantes para responder al usuario."
    ),
)


def main():
    print("Agente AWS Expert listo. Escribe 'salir' para terminar.\n")
    while True:
        user_input = input("Tú: ").strip()
        if user_input.lower() in ("salir", "exit", "quit"):
            print("¡Hasta luego!")
            break
        if not user_input:
            continue
        response = agent(user_input)
        print(f"\nAgente: {response}\n")


if __name__ == "__main__":
    main()
