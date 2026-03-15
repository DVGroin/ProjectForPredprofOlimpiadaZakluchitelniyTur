'''import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import re
def main():


    # Загружаем данные
    data = np.load('путь_к_архиву/train_data.npz')
    train_x = data['train_x']  # массив аудиосигналов, форма (1200, ...)
    train_y_str = data['train_y']  # массив строк (1200,)

    valid_data = np.load('путь_к_архиву/valid_data.npz')
    valid_x = valid_data['valid_x']
    valid_y = valid_data['valid_y']  # уже целые числа (400,)

    # Восстанавливаем метки для train_y
    def extract_number(s):
        # Извлекаем первое целое число из строки
        numbers = re.findall(r'\d+', str(s))
        return int(numbers[0]) if numbers else 0  # fallback, но лучше проверить

    train_y = np.array([extract_number(s) for s in train_y_str])

    # Проверяем количество классов
    num_classes = len(np.unique(train_y))  # предположим, 20
    print(f"Классов: {num_classes}")
    unique, counts = np.unique(train_y, return_counts=True)
    class_distribution = dict(zip(unique, counts))
    # Сохраним для использования в приложении
    np.save('class_distribution.npy', class_distribution)
    max_length = 16000

    def preprocess_audio(audio):
        # Обрезаем/дополняем до max_length
        if len(audio) > max_length:
            audio = audio[:max_length]
        else:
            audio = np.pad(audio, (0, max_length - len(audio)))
        return audio

    train_x_proc = np.array([preprocess_audio(x) for x in train_x])
    valid_x_proc = np.array([preprocess_audio(x) for x in valid_x])

    # Нормализация
    mean = train_x_proc.mean()
    std = train_x_proc.std()
    train_x_proc = (train_x_proc - mean) / std
    valid_x_proc = (valid_x_proc - mean) / std

    # Изменяем форму для 1D CNN: (batch, steps, channels)
    train_x_proc = train_x_proc.reshape(-1, max_length, 1)
    valid_x_proc = valid_x_proc.reshape(-1, max_length, 1)

    # Модель
    model = keras.Sequential([
        layers.Input(shape=(max_length, 1)),
        layers.Conv1D(32, 3, activation='relu'),
        layers.MaxPooling1D(2),
        layers.Conv1D(64, 3, activation='relu'),
        layers.MaxPooling1D(2),
        layers.Conv1D(128, 3, activation='relu'),
        layers.GlobalAveragePooling1D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy'])

    # Обучение
    history = model.fit(train_x_proc, train_y,
                        validation_data=(valid_x_proc, valid_y),
                        epochs=50, batch_size=32,
                        callbacks=[keras.callbacks.EarlyStopping(patience=5)])

    # Сохраняем модель и историю
    model.save('alien_signal_model.h5')
    np.save('history.npy', history.history)
    # Сохраняем распределение классов в валидационном наборе (для топ-5)
    valid_classes, valid_counts = np.unique(valid_y, return_counts=True)
    valid_class_dist = dict(zip(valid_classes, valid_counts))
    np.save('valid_class_dist.npy', valid_class_dist)

    # Сохраняем предсказания для валидационного набора (для графика точности по каждому образцу не требуется, но для теста понадобится)
    # '''