from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import ConversationSerializer, MessageSerializer
from django.core.exceptions import ValidationError
import requests

class WebhookView(APIView):
    """
    Endpoint de webhook para processar eventos de conversas e mensagens.

    Tipos de evento suportados:
      - NEW_CONVERSATION: cria uma nova Conversa com UUID informado.
      - NEW_MESSAGE: adiciona uma Mensagem em uma Conversa aberta.
      - CLOSE_CONVERSATION: encerra uma Conversa, definindo estado como FECHADA.

    Tratamento de erros:
      - Retorna HTTP 400 em caso de payload inválido ou violação de regras de negócio.
    """
    @swagger_auto_schema(
        operation_description="Processa eventos de webhook para conversas e mensagens.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'type': openapi.Schema(type=openapi.TYPE_STRING, enum=['NEW_CONVERSATION','NEW_MESSAGE','CLOSE_CONVERSATION']),
                'timestamp': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                'data': openapi.Schema(type=openapi.TYPE_OBJECT)
            },
            required=['type','timestamp','data']
        ),
        responses={
            200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'status': openapi.Schema(type=openapi.TYPE_STRING)}),
            400: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)})
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Processa requisição POST de webhook.

        Args:
            request: requisição DRF contendo campos `type`, `timestamp` e `data`.

        Retorna:
            HTTP 200 com status 'success' ou HTTP 400 com detalhes do erro.
        """
        event = request.data
        try:
            if event['type'] == 'NEW_CONVERSATION':
                Conversation.objects.create(id=event['data']['id'])
            elif event['type'] == 'NEW_MESSAGE':
                conversation = get_object_or_404(Conversation, id=event['data']['conversation_id'])
                if conversation.status == 'CLOSED':
                    return Response({"error": "Cannot add messages to a closed conversation."}, status=status.HTTP_400_BAD_REQUEST)
                Message.objects.create(
                    id=event['data']['id'],
                    conversation=conversation,
                    direction=event['data']['direction'],
                    content=event['data']['content'],
                    timestamp=event['timestamp']
                )
            elif event['type'] == 'CLOSE_CONVERSATION':
                conversation = get_object_or_404(Conversation, id=event['data']['id'])
                conversation.status = 'CLOSED'
                conversation.save()
            else:
                return Response({"error": "Unknown event type."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({"error": "Duplicate ID detected."}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({"error": "Invalid payload."}, status=status.HTTP_400_BAD_REQUEST)

class ConversationDetailView(APIView):
    """
    Recupera detalhes de uma conversa específica pelo seu UUID.

    A resposta inclui o status da conversa e sua lista de mensagens.
    """
    @swagger_auto_schema(
        operation_description="Recupera os detalhes de uma conversa pelo seu UUID.",
        responses={
            200: ConversationSerializer,
            404: 'Not Found'
        }
    )
    def get(self, request, id, *args, **kwargs):
        """
        Processa requisição GET para obter conversa e suas mensagens.

        Args:
            request: requisição DRF
            id: UUID da conversa a ser recuperada

        Retorna:
            HTTP 200 com dados da conversa ou 404 se não encontrada.
        """
        conversation = get_object_or_404(Conversation, id=id)
        messages = conversation.messages.all().values('id', 'direction', 'content', 'timestamp')
        return Response({
            "id": conversation.id,
            "status": conversation.status,
            "messages": list(messages)
        }, status=status.HTTP_200_OK)

class RootApiView(APIView):
    """
    Endpoint raiz que retorna dados de uma API externa.
    """
    @swagger_auto_schema(
        operation_description="Consulta API pública e retorna o resultado.",
        responses={
            200: openapi.Schema(type=openapi.TYPE_OBJECT),
            503: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)})
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Processa requisição GET na rota raiz e busca dados de API externa.
        """
        return Response({"message": "API está funcionando"}, status=status.HTTP_200_OK)