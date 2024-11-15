# realization/tasks.py
import time

from celery import shared_task
import numpy as np
import matplotlib.pyplot as plt
import io
from celery.contrib.abortable import AbortableTask
from celery.exceptions import Ignore
from django.core.files.base import ContentFile
from .models import MonteCarloIntegrationModel


@shared_task(bind=True, base=AbortableTask)
def perform_monte_carlo_integration(self, user_id, function_expr, lower_bound, upper_bound, num_samples=2500000,
                                    display_fraction=0.001):
    """
    Perform the Monte Carlo integration and save results to the database.
    """
    try:
        # Convert the function expression into a Python lambda
        func = lambda x: eval(function_expr)
        start_time = time.time()
        # Perform Monte Carlo integration with revocation checks
        estimated_area, x_inside, y_inside, x_outside, y_outside = monte_carlo_integration(
            func, lower_bound, upper_bound, num_samples, display_fraction, task=self
        )
        if estimated_area is None:
            raise Ignore()
        end_time = time.time()
        time_needed = round(end_time - start_time, 2)
        # Generate plot and save to the database
        graphic = generate_plot(func, lower_bound, upper_bound, estimated_area, x_inside, y_inside, x_outside,
                                y_outside, function_expr)

        # Save to the database
        monte_carlo_instance = MonteCarloIntegrationModel.objects.create(
            user_id=user_id,
            function=function_expr,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            estimated_area=estimated_area,
            graphic=graphic,
            time_needed=time_needed  # Save execution time
        )

        return {
            'task_id': monte_carlo_instance.id,
            'estimated_area': estimated_area,
        }

    except Exception as e:
        print(f"Error in task: {str(e)}")
        return {'error': str(e)}


# Rest of your functions like monte_carlo_integration() and generate_plot() remain unchanged.


def monte_carlo_integration(func, a, b, num_samples, display_fraction, task=None):
    count_inside = 0
    x_inside = []
    y_inside = []
    x_outside = []
    y_outside = []

    y_min = min(func(x) for x in np.linspace(a, b, 1000))
    y_max = max(func(x) for x in np.linspace(a, b, 1000))

    for i in range(num_samples):
        # Periodically check if the task was revoked
        if task and i % 10000 == 0 and task.is_aborted():
            print("Task was revoked, stopping early.")
            return None, None, None, None, None  # Early return to stop task

        x = np.random.uniform(a, b)
        y = np.random.uniform(y_min, y_max)

        if y <= func(x) and y >= 0:
            count_inside += 1
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

    area = (count_inside / num_samples) * (b - a) * (y_max - y_min)
    return area, x_inside, y_inside, x_outside, y_outside


def generate_plot(func, a, b, estimated_area, x_inside, y_inside, x_outside, y_outside, func_expression):
    # Your existing implementation remains the same
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

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    return ContentFile(buf.read(), name='monte_carlo_plot.png')
