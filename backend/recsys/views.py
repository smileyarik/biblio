from rest_framework import views
from rest_framework.response import Response


class RecPredictView(views.APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get("user_id", None)
        user_id = int(user_id)
        if user_id is None:
            return JsonResponse({})
        responses = {
            1: {
                "recommendations": [{"id": 786, "title": "Красная шапочка", "author": "Перро"}],
                "history": [{"id": 123, "title": "Незнайка на Луне", "author": "Носов"}]
            }
        }
        return Response(responses.get(user_id, {}))

