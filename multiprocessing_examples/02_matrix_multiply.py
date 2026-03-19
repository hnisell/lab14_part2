#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Перемножение матриц с использованием нескольких процессов.
Основано на коде из репозитория 3_Parallelism.
"""

from multiprocessing import Process, Queue
import time
import random

# СПРАВКА: Оригинальный код из 3_Parallelism/matrix_multiply.py
# def element(index, A, B):
#     i, j = index
#     res = 0
#     # получить размерность A (предполагаем, что A и B квадратные)
#     N = len(A[0]) или len(B)
#     for k in range(N):
#         res += A[i][k] * B[k][j]
#     return res
#
# В нашей версии используется очередь для сбора результатов.

def generate_matrix(rows, cols, min_val=0, max_val=5):
    """Генерирует матрицу заданного размера со случайными значениями."""
    return [[random.randint(min_val, max_val) for _ in range(cols)] for _ in range(rows)]

def print_matrix(matrix, name="Матрица"):
    """Красиво выводит матрицу (только если она небольшая)."""
    print(f"\n{name}:")
    for row in matrix:
        print("  ", row)

def element_to_queue(index, A, B, q):
    """
    Вычисляет один элемент результирующей матрицы и помещает результат в очередь.
    
    Аргументы:
        index: кортеж (i, j) - индексы элемента
        A, B: исходные матрицы
        q: очередь multiprocessing.Queue для отправки результата
    """
    i, j = index
    # Предполагаем, что матрицы согласованы: количество столбцов A = количество строк B
    N = len(A[0])  # или len(B)
    res = 0
    for k in range(N):
        res += A[i][k] * B[k][j]
    q.put((index, res))  # отправляем результат в очередь

def multiply_matrices_sequential(A, B):
    """Последовательное перемножение матриц (без распараллеливания)."""
    rows = len(A)
    cols = len(B[0])
    result = [[0 for _ in range(cols)] for _ in range(rows)]
    
    for i in range(rows):
        for j in range(cols):
            for k in range(len(A[0])):
                result[i][j] += A[i][k] * B[k][j]
    return result

def multiply_matrices_parallel(A, B):
    """
    Параллельное перемножение матриц с использованием процессов.
    Каждый элемент вычисляется в отдельном процессе.
    """
    rows = len(A)
    cols = len(B[0])
    result = [[0 for _ in range(cols)] for _ in range(rows)]
    
    # Создаем очередь для сбора результатов
    q = Queue()
    processes = []
    
    # Создаем список всех индексов результирующей матрицы
    indices = [(i, j) for i in range(rows) for j in range(cols)]
    
    # TODO 1: Создать процесс для каждого элемента результирующей матрицы
    # и передать результат через Queue.
    for index in indices:
        p = Process(target=element_to_queue, args=(index, A, B, q))
        processes.append(p)
        p.start()
    
    # Ожидаем завершения всех процессов
    for p in processes:
        p.join()
    
    # Собираем результаты из очереди
    results_received = 0
    while results_received < len(indices):
        index, value = q.get()
        i, j = index
        result[i][j] = value
        results_received += 1
    
    return result

def main():
    """Основная функция для демонстрации перемножения матриц."""
    print("=" * 60)
    print("ПЕРЕМНОЖЕНИЕ МАТРИЦ С ИСПОЛЬЗОВАНИЕМ ПРОЦЕССОВ")
    print("=" * 60)
    
    # Задаем размеры матриц
    rows_A, cols_A = 3, 3  # матрица A: 3x3
    rows_B, cols_B = 3, 3  # матрица B: 3x3 (должна быть cols_A x rows_B)
    
    # Генерируем случайные матрицы
    A = generate_matrix(rows_A, cols_A)
    B = generate_matrix(rows_B, cols_B)
    
    # Выводим исходные матрицы (для небольших размеров)
    if rows_A <= 5 and cols_A <= 5:
        print_matrix(A, "Матрица A")
        print_matrix(B, "Матрица B")
    
    print("\n" + "-" * 40)
    print("ПОСЛЕДОВАТЕЛЬНОЕ ВЫЧИСЛЕНИЕ")
    print("-" * 40)
    
    # TODO 2: Замерить время последовательного и параллельного вычисления
    start_time = time.time()
    result_seq = multiply_matrices_sequential(A, B)
    end_time = time.time()
    seq_time = end_time - start_time
    
    print(f"Время последовательного вычисления: {seq_time:.4f} сек")
    
    if rows_A <= 5 and cols_A <= 5:
        print_matrix(result_seq, "Результат (последовательно)")
    
    print("\n" + "-" * 40)
    print("ПАРАЛЛЕЛЬНОЕ ВЫЧИСЛЕНИЕ (отдельные процессы)")
    print("-" * 40)
    
    start_time = time.time()
    result_par = multiply_matrices_parallel(A, B)
    end_time = time.time()
    par_time = end_time - start_time
    
    print(f"Время параллельного вычисления: {par_time:.4f} сек")
    
    if rows_A <= 5 and cols_A <= 5:
        print_matrix(result_par, "Результат (параллельно)")
    
    print("\n" + "-" * 40)
    print("СРАВНЕНИЕ РЕЗУЛЬТАТОВ")
    print("-" * 40)
    
    # Проверяем, совпадают ли результаты
    if result_seq == result_par:
        print("✓ Результаты совпадают!")
    else:
        print("✗ ОШИБКА: Результаты не совпадают!")
    
    # Вычисляем ускорение
    if par_time > 0:
        speedup = seq_time / par_time
        print(f"Ускорение: {speedup:.2f}x")
    
    print("\n" + "=" * 60)
    print("Анализ эффективности:")
    print(f"  - Всего создано процессов: {rows_A * cols_B}")
    print(f"  - Последовательное время: {seq_time:.4f} сек")
    print(f"  - Параллельное время: {par_time:.4f} сек")
    print(f"  - Ускорение: {seq_time/par_time:.2f}x")
    print("=" * 60)


if __name__ == '__main__':
    main()
    # Раскомментируйте следующую строку для тестирования с разными размерами
    # test_with_different_sizes()