import argparse
import shlex
import sys

def parse_args():
    """
    Разбор аргументов командной строки.
    Возвращает словарь с параметрами конфигурации.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--vfs", help="Путь к VFS", default="")
    parser.add_argument("--script", help="Путь к скрипту", default="")
    args = parser.parse_args()
    return {"vfs_path": args.vfs, "script_path": args.script}

def print_debug_config(config):
    """
    Отладочный вывод параметров при запуске эмулятора.
    """
    print("--- Отладочный вывод параметров ---")
    for key, value in config.items():
        print(f"{key}: {value}")
    print("-----------------------------------")

def cmd_ls(args):
    """
    Заглушка команды ls.
    """
    print("Вызвана команда: ls")
    print(f"Аргументы: {args}")
    return True

def cmd_cd(args):
    """
    Заглушка команды cd.
    Возвращает False при ошибке аргументов для остановки скрипта.
    """
    if len(args) > 1:
        print("Ошибка: cd ожидает не более 1 аргумента")
        return False
    print("Вызвана команда: cd")
    print(f"Аргументы: {args}")
    return True

def cmd_conf_dump(config):
    """
    Служебная команда.
    Выводит параметры в формате ключ-значение.
    """
    for key, value in config.items():
        print(f"{key}={value}")
    return True

def execute_command(command, args, config):
    """
    Маршрутизация команд.
    Возвращает кортеж (успех_выполнения, флаг_продолжения_цикла).
    """
    if command == "exit":
        return True, False
    elif command == "ls":
        return cmd_ls(args), True
    elif command == "cd":
        return cmd_cd(args), True
    elif command == "conf-dump":
        return cmd_conf_dump(config), True
    
    print(f"Ошибка: неизвестная команда '{command}'")
    return False, True

def run_script(script_path, config, vfs_name):
    """
    Исполнение стартового скрипта построчно.
    Остановка при первой ошибке с выводом сообщения.
    """
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                print(f"{vfs_name}:/ $ {line}")
                try:
                    parsed = shlex.split(line)
                    success, _ = execute_command(parsed[0], parsed[1:], config)
                    if not success:
                        print(f"Ошибка исполнения скрипта на строке: {line}")
                        break
                except ValueError as e:
                    print(f"Ошибка синтаксиса в скрипте: {e}")
                    break
    except FileNotFoundError:
        print(f"Ошибка: скрипт '{script_path}' не найден.")

def run_repl(config, vfs_name):
    """
    Цикл интерактивного ввода REPL.
    """
    print("Эмулятор запущен. Введите 'exit' для выхода.")
    while True:
        try:
            user_input = input(f"{vfs_name}:/ $ ").strip()
            if not user_input:
                continue
            
            parsed = shlex.split(user_input)
            _, keep_running = execute_command(parsed[0], parsed[1:], config)
            if not keep_running:
                break
        except ValueError as e:
            print(f"Ошибка синтаксиса: {e}")
        except EOFError:
            print("\nВыход...")
            break
        except KeyboardInterrupt:
            print("\nДля выхода введите 'exit'")

def main():
    """
    Точка входа.
    """
    config = parse_args()
    print_debug_config(config)
    
    vfs_name = "vfs"
    if config["script_path"]:
        run_script(config["script_path"], config, vfs_name)
        
    run_repl(config, vfs_name)

if __name__ == "__main__":
    main()