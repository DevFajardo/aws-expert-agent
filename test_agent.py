"""
Pruebas unitarias para las funciones de tools.py usando pytest.
"""
import json
import pytest
from tools import estimar_costo_lambda, recomendar_arquitectura, buscar_servicio_aws


# ---------------------------------------------------------------------------
# estimar_costo_lambda
# ---------------------------------------------------------------------------

class TestEstimarCostoLambda:
    def test_retorna_total_estimado_usd_valores_normales(self):
        """Verifica que el resultado contiene 'total_estimado_usd' (TOTAL ESTIMADO) con valores normales."""
        resultado = estimar_costo_lambda(1_000_000, 200, 128)
        assert "TOTAL ESTIMADO" in resultado
        assert "USD/mes" in resultado

    def test_retorna_total_estimado_usd_valores_negativos(self):
        """Verifica que el resultado contiene 'total_estimado_usd' incluso con valores negativos."""
        resultado = estimar_costo_lambda(-500, -100, -64)
        assert "TOTAL ESTIMADO" in resultado
        assert "USD/mes" in resultado

    def test_capa_gratuita_sin_costo(self):
        """Con invocaciones dentro de la capa gratuita el costo debe ser $0.0000."""
        resultado = estimar_costo_lambda(500_000, 100, 128)
        assert "$0.0000 USD/mes" in resultado

    def test_incluye_detalle_invocaciones(self):
        """El resultado debe incluir el número de invocaciones."""
        resultado = estimar_costo_lambda(2_000_000, 300, 256)
        assert "2,000,000" in resultado

    def test_retorna_string(self):
        resultado = estimar_costo_lambda(1_000_000, 200, 128)
        assert isinstance(resultado, str)


# ---------------------------------------------------------------------------
# recomendar_arquitectura
# ---------------------------------------------------------------------------

class TestRecomendarArquitectura:
    @pytest.mark.parametrize("caso", ["api_rest", "streaming", "ml_inference", "static_web", "batch"])
    def test_casos_validos_retornan_arquitectura(self, caso):
        """Para cada caso válido debe retornar una descripción de arquitectura."""
        resultado = recomendar_arquitectura(caso)
        assert "Arquitectura recomendada" in resultado
        assert "Patrón" in resultado
        assert "Servicios involucrados" in resultado

    def test_caso_invalido_retorna_opciones_disponibles(self):
        """Para un caso no reconocido debe indicar las opciones disponibles."""
        resultado = recomendar_arquitectura("caso_inexistente")
        assert "no reconocido" in resultado
        assert "Opciones disponibles" in resultado

    def test_caso_invalido_lista_todos_los_casos(self):
        """El mensaje de error debe listar todos los casos soportados."""
        resultado = recomendar_arquitectura("xyz")
        for caso in ["api_rest", "streaming", "ml_inference", "static_web", "batch"]:
            assert caso in resultado

    def test_api_rest_incluye_lambda(self):
        resultado = recomendar_arquitectura("api_rest")
        assert "Lambda" in resultado

    def test_case_insensitive(self):
        """La función debe ser insensible a mayúsculas."""
        resultado = recomendar_arquitectura("API_REST")
        assert "Arquitectura recomendada" in resultado


# ---------------------------------------------------------------------------
# buscar_servicio_aws
# ---------------------------------------------------------------------------

class TestBuscarServicioAws:
    @pytest.mark.parametrize("categoria", ["compute", "storage", "database", "ai", "networking"])
    def test_categorias_validas_retornan_lista_servicios(self, categoria):
        """Para cada categoría válida debe retornar una lista de servicios."""
        resultado = buscar_servicio_aws(categoria)
        assert f"categoría '{categoria}'" in resultado
        assert "•" in resultado

    def test_categoria_invalida_retorna_categorias_disponibles(self):
        """Para una categoría no reconocida debe indicar las categorías disponibles."""
        resultado = buscar_servicio_aws("categoria_invalida")
        assert "no reconocida" in resultado
        assert "Opciones disponibles" in resultado

    def test_categoria_invalida_lista_todas_las_categorias(self):
        """El mensaje de error debe listar todas las categorías soportadas."""
        resultado = buscar_servicio_aws("xyz")
        for cat in ["compute", "storage", "database", "ai", "networking"]:
            assert cat in resultado

    def test_compute_incluye_lambda(self):
        resultado = buscar_servicio_aws("compute")
        assert "Lambda" in resultado

    def test_ai_incluye_bedrock(self):
        resultado = buscar_servicio_aws("ai")
        assert "Bedrock" in resultado

    def test_case_insensitive(self):
        """La función debe ser insensible a mayúsculas."""
        resultado = buscar_servicio_aws("COMPUTE")
        assert "categoría 'compute'" in resultado
