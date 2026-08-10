"""Tests de la integración con el entorno de demo de Nexus.

Se centran en lo que puede romperse en silencio: el formato del tenant_id que
el gate valida por longitud, los topes de vigencia, y el manejo de una
configuración ausente —que es el estado normal en local y en los tests—.
"""

import pytest
from pydantic import ValidationError

from app.core import nexus_demo as nexus
from app.core.config import missing_nexus_demo_config
from app.schemas.nexus_demos import NexusDemoCreate, NexusDemoExtend


class TestTenantId:
    def test_formato(self):
        tenant = nexus.generate_tenant_id()
        assert tenant.startswith("demo-")
        assert tenant == tenant.lower()

    def test_cabe_en_el_limite_del_gate(self):
        # invites.tenant_id tiene CHECK char_length BETWEEN 1 AND 64.
        assert 1 <= len(nexus.generate_tenant_id()) <= 64

    def test_no_se_repite(self):
        generados = {nexus.generate_tenant_id() for _ in range(200)}
        assert len(generados) == 200


class TestBaseUrl:
    def test_quita_la_barra_final(self, monkeypatch):
        monkeypatch.setattr(
            "app.core.nexus_demo.settings.NEXUS_DEMO_OPS_URL",
            "https://demo.example.com/",
        )
        assert nexus._base_url() == "https://demo.example.com"

    def test_sin_url_falla_con_mensaje_claro(self, monkeypatch):
        monkeypatch.setattr("app.core.nexus_demo.settings.NEXUS_DEMO_OPS_URL", "")
        with pytest.raises(nexus.NexusDemoError) as exc:
            nexus._base_url()
        assert "NEXUS_DEMO_OPS_URL" in str(exc.value)

    def test_sin_secreto_falla_con_mensaje_claro(self, monkeypatch):
        monkeypatch.setattr("app.core.nexus_demo.settings.GATE_INTERNAL_SECRET", "")
        with pytest.raises(nexus.NexusDemoError) as exc:
            nexus._headers()
        assert "GATE_INTERNAL_SECRET" in str(exc.value)

    def test_cabecera_bearer(self, monkeypatch):
        monkeypatch.setattr(
            "app.core.nexus_demo.settings.GATE_INTERNAL_SECRET", "s3cr3t"
        )
        assert nexus._headers()["Authorization"] == "Bearer s3cr3t"


class TestConfigAusente:
    def test_reporta_las_dos(self, monkeypatch):
        monkeypatch.setattr("app.core.config.settings.NEXUS_DEMO_OPS_URL", "")
        monkeypatch.setattr("app.core.config.settings.GATE_INTERNAL_SECRET", "")
        assert set(missing_nexus_demo_config()) == {
            "NEXUS_DEMO_OPS_URL",
            "GATE_INTERNAL_SECRET",
        }

    def test_configurada_no_reporta_nada(self, monkeypatch):
        monkeypatch.setattr(
            "app.core.config.settings.NEXUS_DEMO_OPS_URL", "https://demo.example.com"
        )
        monkeypatch.setattr("app.core.config.settings.GATE_INTERNAL_SECRET", "s3cr3t")
        assert missing_nexus_demo_config() == []


class TestVigencia:
    def test_por_defecto_siete_dias(self):
        payload = NexusDemoCreate(company_name="ACME", recipient_email="ops@acme.mx")
        assert payload.ttl_hours == 168

    @pytest.mark.parametrize("horas", [0, -1, 337, 10_000])
    def test_rechaza_fuera_del_rango(self, horas):
        with pytest.raises(ValidationError):
            NexusDemoCreate(
                company_name="ACME",
                recipient_email="ops@acme.mx",
                ttl_hours=horas,
            )

    @pytest.mark.parametrize("horas", [1, 72, 168, 336])
    def test_acepta_dentro_del_rango(self, horas):
        payload = NexusDemoCreate(
            company_name="ACME", recipient_email="ops@acme.mx", ttl_hours=horas
        )
        assert payload.ttl_hours == horas

    def test_extender_tiene_el_mismo_tope(self):
        with pytest.raises(ValidationError):
            NexusDemoExtend(ttl_hours=337)
        assert NexusDemoExtend(ttl_hours=336).ttl_hours == 336


class TestValidacionDeEntrada:
    def test_email_invalido(self):
        with pytest.raises(ValidationError):
            NexusDemoCreate(company_name="ACME", recipient_email="no-es-un-email")

    def test_empresa_vacia(self):
        with pytest.raises(ValidationError):
            NexusDemoCreate(company_name="", recipient_email="ops@acme.mx")
