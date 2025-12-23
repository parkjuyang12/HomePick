# chatbot/views.py
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import APIException

from .responder import ChatbotResponder

logger = logging.getLogger(__name__)
responder = ChatbotResponder()

class ChatbotView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        logger.error("🔥 ChatbotView POST called")
        logger.error(f"payload: {request.data}")

        user_message = request.data.get("message")
        if not user_message:
            return Response(
                {"error": "message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            answer = responder.respond(user_message)
            return Response({"answer": answer})

        except Exception as e:
            logger.exception("🔥 Chatbot internal error")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
