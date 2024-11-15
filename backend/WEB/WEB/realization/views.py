from celery.contrib.abortable import AbortableAsyncResult
from celery.result import AsyncResult
from celery.worker.control import revoke
from django.contrib.auth import login, logout as auth_logout, authenticate
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView
from .models import MonteCarloIntegrationModel
from .serializers import MonteCarloSerializer
import matplotlib
from .tasks import perform_monte_carlo_integration

matplotlib.use("Agg")


class HomeView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MonteCarloSerializer
    queryset = MonteCarloIntegrationModel.objects.all()

    def get(self, request, *args, **kwargs):
        # Retrieve the user's previous solutions
        user = self.request.user
        solutions = MonteCarloIntegrationModel.objects.filter(user=user).all()
        serializer = self.serializer_class(solutions, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        function_expr = request.data.get("function")
        lower_bound = float(request.data.get("lower_bound"))
        upper_bound = float(request.data.get("upper_bound"))

        # Call the Celery task asynchronously
        task = perform_monte_carlo_integration.delay(user.id, function_expr, lower_bound, upper_bound)
        return Response({'task_id': task.id, 'status': 'Task is processing'}, status=status.HTTP_202_ACCEPTED)


class TaskStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id, *args, **kwargs):
        task = AbortableAsyncResult(task_id)

        if task:
            response_data = {
                'task_id': task.id,
                'status': task.state,
                'result': None,  # Default to None
            }
            # Populate result if the task is successful
            if task.state == 'SUCCESS' and isinstance(task.result, dict) and len(task.result) != 1:
                id = task.result.get('task_id')
                monte_carlo_obj = MonteCarloIntegrationModel.objects.filter(id=id).first()
                response_data['result'] = {
                    'id': task.result.get('task_id'),  # Use task_id from result
                    'function': monte_carlo_obj.function,
                    'lower_bound': monte_carlo_obj.lower_bound,
                    'upper_bound': monte_carlo_obj.upper_bound,
                    'estimated_area': task.result.get('estimated_area'),
                    'graphic_url': monte_carlo_obj.get_graphic(),  # Get the URL for the graphic
                    'time_needed': monte_carlo_obj.time_needed,
                }
            elif task.state == 'SUCCESS' and isinstance(task.result, dict) and len(task.result) == 1:
                response_data = {
                    'status': "Canceled",
                    "result": "Task was canceled."
                }
            return Response(response_data, status=status.HTTP_200_OK)

        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


class Delete_Task_View(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id, *args, **kwargs):

        task = AbortableAsyncResult(task_id)
        # Check if the task is still revocable
        if task.state in ["SUCCESS", "FAILURE", "REVOKED"]:
            return Response({"error": "Task is already completed and cannot be revoked."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Attempt to revoke the task
            task.abort()
            return Response({"result": "The task was canceled."})
        except Exception as e:
            return Response({"error": f"Failed to revoke task: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignUpView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Signup successful! You can now log in.",
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({})

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful!",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


def logout_view(request):
    auth_logout(request)
    return redirect(reverse('realization:login'))



