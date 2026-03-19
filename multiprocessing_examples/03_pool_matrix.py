#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Перемножение матриц с использованием пула процессов (Pool).
Демонстрирует эффективное распределение задач между фиксированным числом процессов.
"""

from multiprocessing import Pool
import time
import random
import os

def generate_matrix(rows, cols, min_val=0, max_val=5):
    """Генерирует матрицу заданного размера со случайными значениями."""
    return [[random.randint(min_val, max_val) for _ in range(cols)] for _ in range(rows)]

def print_matrix(matrix, name="Матрица"):
    """Красиво выводит матрицу (только если она небольшая)."""
    print(f"\n{name}:")
    for row in matrix:
        print("  ", row)

# ИСПРАВЛЕНО: функция принимает 4 аргумента для starmap
def element(i, j, A, B):
    """
    Вычисляет один элемент результирующей матрицы.
    
    Аргументы:
        i, j: индексы элемента
        A, B: исходные матрицы
    
    Возвращает:
        Кортеж (i, j, значение) для сборки результата
    """
    N = len(A[0])  # количество столбцов A = количество строк B
    res = 0
    for k in range(N):
        res += A[i][k] * B[k][j]
    return (i, j, res)

# Альтернативная версия с одним аргументом (для map)
def element_with_args(args):
    """Версия функции, принимающая один кортеж аргументов (для map)."""
    i, j, A, B = args
    return element(i, j, A, B)

def multiply_matrices_sequential(A, B):
    """Последовательное перемножение матриц (базовый вариант)."""
    rows = len(A)
    cols = len(B[0])
    result = [[0 for _ in range(cols)] for _ in range(rows)]
    
    for i in range(rows):
        for j in range(cols):
            for k in range(len(A[0])):
                result[i][j] += A[i][k] * B[k][j]
    return result

def multiply_matrices_pool(A, B, num_processes=None):
    """
    Параллельное перемножение матриц с использованием пула процессов.
    
    Аргументы:
        A, B: исходные матрицы
        num_processes: количество процессов в пуле (если None, используется cpu_count())
    
    Возвращает:
        Результирующую матрицу
    """
    rows = len(A)
    cols = len(B[0])
    
    # Создаем список аргументов для каждой задачи
    # Для starmap каждый элемент должен быть кортежем аргументов
    args = [(i, j, A, B) for i in range(rows) for j in range(cols)]
    
    print(f"  Всего задач: {len(args)}")
    print(f"  Процессов в пуле: {num_processes if num_processes else 'авто'}")
    
    # TODO 3: Использовать Pool.starmap() для параллельного вычисления
    # Подсказка: with Pool(processes=num_processes) as pool: 
    #            results = pool.starmap(element, args)
    with Pool(processes=num_processes) as pool:
        # ИСПРАВЛЕНО: element теперь принимает 4 аргумента, starmap распакует кортежи
        results = pool.starmap(element, args)
    
    # Собираем результаты в матрицу
    result = [[0 for _ in range(cols)] for _ in range(rows)]
    for i, j, value in results:
        result[i][j] = value
    
    return result

def multiply_matrices_pool_map(A, B, num_processes=None):
    """
    Альтернативная версия с использованием map() вместо starmap().
    Требует упаковки всех аргументов в один кортеж.
    """
    rows = len(A)
    cols = len(B[0])
    
    # Для map() нужно упаковать все аргументы в один кортеж
    args = [(i, j, A, B) for i in range(rows) for j in range(cols)]
    
    with Pool(processes=num_processes) as pool:
        # map ожидает функцию с одним аргументом
        results = pool.map(element_with_args, args)
    
    result = [[0 for _ in range(cols)] for _ in range(rows)]
    for i, j, value in results:
        result[i][j] = value
    
    return result

def demonstrate_pool_usage():
    """Демонстрация использования пула процессов с разным количеством процессов."""
    
    print("=" * 70)
    print("ПЕРЕМНОЖЕНИЕ МАТРИЦ С ИСПОЛЬЗОВАНИЕМ ПУЛА ПРОЦЕССОВ")
    print("=" * 70)
    
    # Создаем матрицы среднего размера для наглядного сравнения
    size = 10
    print(f"\nГенерация матриц размером {size}x{size}...")
    
    A = generate_matrix(size, size)
    B = generate_matrix(size, size)
    
    print("\n" + "-" * 70)
    print("ПОСЛЕДОВАТЕЛЬНОЕ ВЫЧИСЛЕНИЕ (для сравнения)")
    print("-" * 70)
    
    start_time = time.time()
    result_seq = multiply_matrices_sequential(A, B)
    seq_time = time.time() - start_time
    print(f"Время последовательного вычисления: {seq_time:.4f} сек")
    
    print("\n" + "-" * 70)
    print("ПАРАЛЛЕЛЬНОЕ ВЫЧИСЛЕНИЕ С ПУЛОМ ПРОЦЕССОВ")
    print("-" * 70)
    
    # TODO 4: Запустить с разным числом процессов (1, 2, 4) и сравнить время
    processes_to_test = [1, 2, 4]
    results = {}
    
    for num_proc in processes_to_test:
        print(f"\n>>> Тест с {num_proc} процесс(ами) в пуле:")
        
        start_time = time.time()
        result_pool = multiply_matrices_pool(A, B, num_processes=num_proc)
        pool_time = time.time() - start_time
        
        results[num_proc] = {
            'time': pool_time,
            'speedup': seq_time / pool_time if pool_time > 0 else 0,
            'correct': result_seq == result_pool
        }
        
        print(f"  Время выполнения: {pool_time:.4f} сек")
        print(f"  Ускорение: {seq_time/pool_time:.2f}x")
        print(f"  Результат верный: {'✓' if result_seq == result_pool else '✗'}")
    
    print("\n" + "=" * 70)
    print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print("=" * 70)
    print(f"{'Процессов':^10} | {'Время (сек)':^12} | {'Ускорение':^10} | {'Корректно':^9}")
    print("-" * 70)
    
    for num_proc in processes_to_test:
        res = results[num_proc]
        print(f"{num_proc:^10} | {res['time']:^12.4f} | {res['speedup']:^10.2f}x | {str(res['correct']):^9}")
    
    print("=" * 70)

def test_with_large_matrix():
    """Тестирование с большой матрицей для демонстрации эффективности пула."""
    
    print("\n\n" + "=" * 70)
    print("ТЕСТИРОВАНИЕ С БОЛЬШОЙ МАТРИЦЕЙ (20x20)")
    print("=" * 70)
    
    size = 20
    print(f"Генерация матриц {size}x{size}...")
    
    A = generate_matrix(size, size)
    B = generate_matrix(size, size)
    
    # Последовательное вычисление
    print("\nПоследовательное вычисление...")
    start = time.time()
    result_seq = multiply_matrices_sequential(A, B)
    seq_time = time.time() - start
    print(f"  Время: {seq_time:.4f} сек")
    
    # Тестируем разные размеры пула
    pool_sizes = [2, 4, 8]
    
    print("\nРезультаты с пулом процессов:")
    print("-" * 50)
    print(f"{'Пул':^6} | {'Время':^10} | {'Ускорение':^10} | {'Эффективность':^12}")
    print("-" * 50)
    
    for pool_size in pool_sizes:
        start = time.time()
        result_pool = multiply_matrices_pool(A, B, num_processes=pool_size)
        pool_time = time.time() - start
        
        speedup = seq_time / pool_time
        efficiency = speedup / pool_size * 100  # эффективность использования процессов
        
        print(f"{pool_size:^6} | {pool_time:^10.4f} | {speedup:^10.2f}x | {efficiency:^11.1f}%")
        
        if result_seq != result_pool:
            print(f"  ⚠ ВНИМАНИЕ: Результаты не совпадают для {pool_size} процессов!")

def demonstrate_pool_advantages():
    """Демонстрация преимуществ пула перед созданием отдельных процессов."""
    
    print("\n\n" + "=" * 70)
    print("ПРЕИМУЩЕСТВА ПУЛА ПРОЦЕССОВ")
    print("=" * 70)
    
    print("""
Пул процессов (Pool) предоставляет следующие преимущества:

1. ПЕРЕИСПОЛЬЗОВАНИЕ ПРОЦЕССОВ:
   - Процессы создаются один раз и используются для множества задач
   - Нет накладных расходов на создание процесса для каждой задачи

2. АВТОМАТИЧЕСКОЕ РАСПРЕДЕЛЕНИЕ ЗАДАЧ:
   - Пул сам распределяет задачи между процессами
   - Балансировка нагрузки происходит автоматически

3. УДОБНЫЙ ИНТЕРФЕЙС:
   - map(), starmap(), apply_async() - готовые методы для распараллеливания
   - Автоматический сбор результатов

4. КОНТРОЛЬ НАГРУЗКИ:
   - Можно ограничить количество одновременно работающих процессов
   - Предотвращает перегрузку системы

5. ОБРАБОТКА РЕЗУЛЬТАТОВ:
   - Результаты возвращаются в удобном виде
   - Не нужно использовать Queue или Pipe вручную
    """)

def main():
    """Основная функция."""
    
    print("Лабораторная работа 14 - Задание А2: Пул процессов")
    print("Автор: Студент")
    print("Группа: ...")
    print()
    
    # Основная демонстрация
    demonstrate_pool_usage()
    
    # Дополнительные тесты
    print("\n\nХотите выполнить дополнительное тестирование с большой матрицей? (y/n)")
    answer = input("> ").lower()
    if answer == 'y':
        test_with_large_matrix()
    
    # Демонстрация преимуществ
    print("\n\nХотите увидеть преимущества пула процессов? (y/n)")
    answer = input("> ").lower()
    if answer == 'y':
        demonstrate_pool_advantages()
    
    print("\n" + "=" * 70)
    print("РАБОТА ЗАВЕРШЕНА")
    print("=" * 70)

def advanced_analysis():
    """Продвинутый анализ для любознательных."""
    
    print("\n\n" + "=" * 70)
    print("ПРОДВИНУТЫЙ АНАЛИЗ ЭФФЕКТИВНОСТИ")
    print("=" * 70)
    
    sizes = [5, 10, 15, 20, 25]
    pool_configs = [1, 2, 4, 8]
    
    print("\nАнализ зависимости времени от размера матрицы и размера пула:")
    print("(значения - время в секундах)")
    
    # Заголовок таблицы
    print("\nРазмер |", end="")
    for p in pool_configs:
        print(f" Пул={p:2} |", end="")
    print()
    print("-" * 60)
    
    for size in sizes:
        print(f"{size:3}x{size:3} |", end="")
        A = generate_matrix(size, size)
        B = generate_matrix(size, size)
        
        for pool_size in pool_configs:
            start = time.time()
            multiply_matrices_pool(A, B, num_processes=pool_size)
            exec_time = time.time() - start
            print(f" {exec_time:7.4f} |", end="")
        print()

if __name__ == '__main__':
    main()
    
    # Раскомментируйте для продвинутого анализа
    # print("\n\nЗапустить продвинутый анализ? (y/n)")
    # if input("> ").lower() == 'y':
    #     advanced_analysis()