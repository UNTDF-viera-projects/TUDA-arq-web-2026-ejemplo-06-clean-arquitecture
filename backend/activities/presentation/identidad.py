from ..domain.modelos import Participante
from ..models import Participant


def participante_actual(usuario) -> Participante:
    """Traduce el usuario autenticado al participante del dominio."""
    nombre = usuario.get_full_name() or usuario.username
    fila, _ = Participant.objects.get_or_create(
        user=usuario,
        defaults={"name": nombre},
    )
    return Participante(id=fila.id, nombre=nombre, email=(usuario.email or "").strip())
