from django.db import models
from django.core.exceptions import ValidationError

class Conversation(models.Model):
    """
    Modelo que representa uma conversa.

    Atributos:
      - id: UUID único da conversa.
      - status: estado da conversa, pode ser 'OPEN' ou 'CLOSED'.
      - created_at: timestamp de criação.
      - updated_at: timestamp da última atualização.
    """
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    ]

    id = models.UUIDField(primary_key=True, unique=True, editable=False)
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id} - {self.status}"

class Message(models.Model):
    """
    Modelo que representa uma mensagem pertencente a uma conversa.

    Atributos:
      - id: UUID único da mensagem.
      - conversation: referência à conversa associada.
      - direction: direção da mensagem, 'SENT' ou 'RECEIVED'.
      - content: conteúdo textual da mensagem.
      - timestamp: data e hora em que a mensagem foi enviada/recebida.
    """
    DIRECTION_CHOICES = [
        ('SENT', 'Sent'),
        ('RECEIVED', 'Received'),
    ]

    id = models.UUIDField(primary_key=True, unique=True, editable=False)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    direction = models.CharField(max_length=9, choices=DIRECTION_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField()

    def clean(self):
        if self.conversation.status == 'CLOSED':
            raise ValidationError("Cannot add message to a closed conversation.")

    def save(self, *args, **kwargs):
        # validate before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message {self.id} - {self.direction}"