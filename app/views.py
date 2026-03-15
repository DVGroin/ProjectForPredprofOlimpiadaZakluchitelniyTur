from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django import forms
from django.contrib.auth.models import User
from .models import Profile
import numpy as np
import json
import tempfile
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .models import Profile
from .forms import UserCreationForm
#from tensorflow.keras.models import load_model
import plotly.graph_objs as go
import plotly.utils

# Загрузка обученной модели и данных
BASE_DIR = settings.BASE_DIR
'''
#model = load_model(os.path.join(BASE_DIR, 'alien_signal_model.h5'))
history = np.load(os.path.join(BASE_DIR, 'history.npy'), allow_pickle=True).item()
class_dist = np.load(os.path.join(BASE_DIR, 'class_distribution.npy'), allow_pickle=True).item()
valid_class_dist = np.load(os.path.join(BASE_DIR, 'valid_class_dist.npy'), allow_pickle=True).item()
preproc_params = np.load(os.path.join(BASE_DIR, 'preproc_params.npy'), allow_pickle=True).item()

max_length = preproc_params['max_length']
mean = preproc_params['mean']
std = preproc_params['std']
'''
'''
def preprocess_audio(audio):
    """Функция предобработки аудио (должна совпадать с использованной при обучении)"""
    if len(audio) > max_length:
        audio = audio[:max_length]
    else:
        audio = np.pad(audio, (0, max_length - len(audio)))
    return audio
'''
# Представления
'''
class CustomLoginView(LoginView):
    template_name = 'login.html'

class CustomLogoutView(LogoutView):
    pass

@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})

@login_required
def analytics(request):
    """Страница с графиками"""
    # График точности на валидации по эпохам
    val_acc = history.get('val_accuracy', [])
    epochs = list(range(1, len(val_acc)+1))
    acc_chart = {
        'data': [go.Scatter(x=epochs, y=val_acc, mode='lines', name='Точность на валидации')],
        'layout': go.Layout(title='Точность на валидации по эпохам',
                            xaxis={'title': 'Эпоха'},
                            yaxis={'title': 'Точность'})
    }

    # Распределение классов в обучающем наборе
    classes = [str(k) for k in class_dist.keys()]
    counts = list(class_dist.values())
    dist_chart = {
        'data': [go.Bar(x=classes, y=counts)],
        'layout': go.Layout(title='Распределение классов в обучающем наборе',
                            xaxis={'title': 'Класс'},
                            yaxis={'title': 'Количество записей'})
    }

    # Топ-5 классов в валидационном наборе
    sorted_valid = sorted(valid_class_dist.items(), key=lambda x: x[1], reverse=True)[:5]
    top_classes = [str(c[0]) for c in sorted_valid]
    top_counts = [c[1] for c in sorted_valid]
    top_chart = {
        'data': [go.Bar(x=top_classes, y=top_counts)],
        'layout': go.Layout(title='Топ-5 классов в валидационном наборе',
                            xaxis={'title': 'Класс'},
                            yaxis={'title': 'Количество записей'})
    }

    context = {
        'acc_chart': json.dumps(acc_chart, cls=plotly.utils.PlotlyJSONEncoder),
        'dist_chart': json.dumps(dist_chart, cls=plotly.utils.PlotlyJSONEncoder),
        'top_chart': json.dumps(top_chart, cls=plotly.utils.PlotlyJSONEncoder),
    }
    return render(request, 'analytics.html', context)

@login_required
def upload_test(request):
    """Загрузка тестового .npz файла и отображение результатов"""
    if request.method == 'POST' and request.FILES.get('test_file'):
        test_file = request.FILES['test_file']
        # Сохраняем во временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.npz') as tmp:
            for chunk in test_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            data = np.load(tmp_path)
            test_x = data['test_x']
            test_y = data['test_y']
        except Exception as e:
            return HttpResponse(f"Ошибка при загрузке файла: {e}", status=400)
        finally:
            os.unlink(tmp_path)  # удаляем временный файл

        # Предобработка
        test_x_proc = np.array([preprocess_audio(x) for x in test_x])
        test_x_proc = (test_x_proc - mean) / std
        test_x_proc = test_x_proc.reshape(-1, max_length, 1)

        # Предсказания
        predictions = model.predict(test_x_proc)
        pred_classes = np.argmax(predictions, axis=1)
        accuracy = np.mean(pred_classes == test_y)
        # Вычисляем loss (sparse categorical crossentropy)
        import tensorflow as tf
        loss = tf.keras.losses.sparse_categorical_crossentropy(test_y, predictions).numpy().mean()

        # Диаграмма точности по каждому образцу (правильно/неправильно)
        correct = (pred_classes == test_y).astype(int)
        per_sample_chart = {
            'data': [go.Bar(x=list(range(len(test_y))), y=correct,
                            marker_color=['green' if c == 1 else 'red' for c in correct])],
            'layout': go.Layout(title='Точность по каждому тестовому образцу (зелёный — верно)',
                                xaxis={'title': 'Номер образца'},
                                yaxis={'title': 'Верно/неверно'})
        }

        context = {
            'accuracy': accuracy,
            'loss': loss,
            'per_sample_chart': json.dumps(per_sample_chart, cls=plotly.utils.PlotlyJSONEncoder),
        }
        return render(request, 'test_results.html', context)

    return render(request, 'upload_test.html')

@staff_member_required
def create_user(request):
    """Создание нового пользователя (только для администратора)"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            user = User.objects.create_user(username=username, password=password)
            Profile.objects.create(user=user, role='user',
                                   first_name=first_name, last_name=last_name)
            return redirect('user_list')  # мы создадим этот URL позже
    else:
        form = UserCreationForm()
    return render(request, 'create_user.html', {'form': form})

@staff_member_required
def user_list(request):
    """Список пользователей для администратора (необязательно, но удобно)"""
    users = User.objects.filter(profile__role='user').select_related('profile')
    return render(request, 'user_list.html', {'users': users})
'''


# Create your views here.
def test_view(request):
    return render(request, "123.html")

def upload_audio(request):
    if request.method == 'POST' and request.FILES.get('audio_file'):
        audio_file = request.FILES['audio_file']
        
        # Проверка расширения (по желанию)
        ext = os.path.splitext(audio_file.name)[1].lower()
        allowed = ['.mp3', '.wav', '.ogg', '.m4a', '.flac']
        if ext not in allowed:
            return HttpResponse('Неподдерживаемый формат файла', status=400)

        # Сохраняем файл в папку media/uploads/
        file_path = default_storage.save(f'uploads/{audio_file.name}', audio_file)
        
        # Здесь можно добавить логику обработки файла, сохранить ссылку в БД и т.д.
        # Например: AudioFile.objects.create(file=file_path, ...)

        return HttpResponse(f'Файл успешно загружен: {file_path}')
    
    # GET-запрос — показываем форму
    return render(request, 'upload_audio.html')


class UserCreationForm(forms.Form):
    username = forms.CharField(max_length=150, label='Логин')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    first_name = forms.CharField(max_length=100, label='Имя')
    last_name = forms.CharField(max_length=100, label='Фамилия')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует')
        return username