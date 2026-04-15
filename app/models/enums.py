from enum import StrEnum


class UserRole(StrEnum):
    adm = "adm"
    gerente = "gerente"
    usuario = "usuario"
    # Valor legado usado nas primeiras versões. Mantido para leitura segura
    # de bancos que já tinham usuário inicial com role "admin".
    admin = "admin"


class ClientStatus(StrEnum):
    ativo = "ativo"
    inativo = "inativo"


class ContractStatus(StrEnum):
    rascunho = "rascunho"
    em_edicao = "em_edicao"
    gerado = "gerado"
    enviado = "enviado"
    visualizado = "visualizado"
    aguardando_assinatura = "aguardando_assinatura"
    assinado = "assinado"
    cancelado = "cancelado"
    expirado = "expirado"


class SignatureStatus(StrEnum):
    completed = "completed"
    rejected = "rejected"


class ActorType(StrEnum):
    admin = "admin"
    public_signer = "public_signer"
    system = "system"


class NotificationChannel(StrEnum):
    whatsapp = "whatsapp"
    email = "email"
    webhook = "webhook"


class NotificationStatus(StrEnum):
    pending = "pending"
    sent = "sent"
    failed = "failed"
