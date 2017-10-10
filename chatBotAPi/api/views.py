from api import methods
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def chat_data(request):
    text = request.data.get('text')
    session_id = request.data.get('sessionId')
    if text and session_id:
        try:
            response = methods.process_request(text, session_id)
            return Response(status=status.HTTP_200_OK,
                            data={"response": response, "status": status.HTTP_200_OK})
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data={"success": False, "error": e})
    else:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"success": False,
                  "error": "name is required fields."})
