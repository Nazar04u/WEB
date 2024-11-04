import time
from datetime import timedelta

from django.contrib.auth import login, logout as auth_logout, authenticate
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView
from .models import MonteCarloIntegrationModel
from .serializers import MonteCarloSerializer
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import io
from django.core.files.base import ContentFile

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
        num_samples = 2500000  # Set a default if not provided
        display_fraction = 0.001
        try:
            # Convert the function expression into a Python lambda
            func = lambda x: eval(function_expr)

            # Perform Monte Carlo integration
            start_time = time.time()
            estimated_area, x_inside, y_inside, x_outside, y_outside = self.monte_carlo_integration(
                func, lower_bound, upper_bound, num_samples, display_fraction
            )

            # Generate plot as a PNG image and save to a Django file
            graphic = self.generate_plot(func, lower_bound, upper_bound, estimated_area, x_inside, y_inside, x_outside,
                                         y_outside, func_expression=function_expr)
            end_time = time.time()
            time_needed = round(end_time - start_time, 2)
            # Save to the database
            monte_carlo_instance = MonteCarloIntegrationModel.objects.create(
                user=user,
                function=function_expr,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                estimated_area=estimated_area,
                graphic=graphic,
                time_needed=time_needed
            )

            # Serialize and return the response
            serializer = self.serializer_class(monte_carlo_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def monte_carlo_integration(self, func, a, b, num_samples, display_fraction):
        """
        Perform the Monte Carlo integration and return estimated area and coordinates for plotting.
        """
        count_inside = 0
        x_inside = []
        y_inside = []
        x_outside = []
        y_outside = []

        # Determine the minimum and maximum y-values on the interval [a, b]
        y_min = min(func(x) for x in np.linspace(a, b, 1000))
        y_max = max(func(x) for x in np.linspace(a, b, 1000))

        for i in range(num_samples):
            x = np.random.uniform(a, b)
            y = np.random.uniform(y_min, y_max)

            if y <= func(x) and y >= 0:
                count_inside += 1
                # Append points based on display_fraction to reduce points on plot
                if i % int(1 / display_fraction) == 0:
                    x_inside.append(x)
                    y_inside.append(y)
            elif y >= func(x) and y <= 0:
                count_inside += 1
                if i % int(1 / display_fraction) == 0:
                    x_inside.append(x)
                    y_inside.append(y)
            else:
                if i % int(1 / display_fraction) == 0:
                    x_outside.append(x)
                    y_outside.append(y)

        # Calculate the area
        area = (count_inside / num_samples) * (b - a) * (y_max - y_min)
        return area, x_inside, y_inside, x_outside, y_outside

    def generate_plot(self, func, a, b, estimated_area, x_inside, y_inside, x_outside, y_outside, func_expression):
        """
        Generate a plot of the Monte Carlo integration process, save it as a PNG image,
        and return a Django `ContentFile` for storage in the model.
        """
        x = np.linspace(a, b, 100)
        y = func(x)

        plt.figure(figsize=(10, 6))
        plt.plot(x, y, label=f'y = {func_expression}', color='blue')
        plt.fill_between(x, y, color='lightblue', alpha=0.5)
        plt.scatter(x_inside, y_inside, color='green', s=1, label='Points Inside')
        plt.scatter(x_outside, y_outside, color='red', s=1, label='Points Outside')
        plt.title(f'Monte Carlo Integration\nEstimated Area: {estimated_area:.4f}')
        plt.xlabel('x')
        plt.ylabel(f'{func_expression}')
        plt.legend()
        plt.grid()

        # Save the plot to an in-memory file
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)

        # Create a Django file from the in-memory file
        return ContentFile(buf.read(), name='monte_carlo_plot.png')


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



