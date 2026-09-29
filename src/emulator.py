import argparse
import shlex
import os
import zipfile

def parse_args():
    """Разбор аргументов командной строки."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--vfs", help="Путь к VFS (zip-архив)", default="")
    parser.add_argument("--script", help="Путь к скрипту", default="")
    args = parser.parse_args()
    return {"vfs_path": args.vfs, "script_path": args.script}

def print_debug_config(config):
    """Отладочный вывод параметров при запуске эмулятора."""
    print("--- Отладочный вывод параметров ---")
    for key, value in config.items():
        print(f"{key}: {value}")
    print("-----------------------------------")

def load_vfs(zip_path):
    """Загружает список всех путей из ZIP-архива."""
    if not zip_path or not os.path.exists(zip_path):
        print(f"Внимание: VFS '{zip_path}' не найден. Папки будут пустыми.")
        return []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            return zf.namelist()
    except zipfile.BadZipFile:
        print("Ошибка: файл VFS не является корректным ZIP-архивом.")
        return []

def cmd_ls(args, state):
    """Выводит список файлов и папок в текущей директории."""
    prefix = state['cwd'].lstrip('/')
    if prefix and not prefix.endswith('/'):
        prefix += '/'
        
    items = set()
    for f in state['files']:
        if f.startswith(prefix):
            rest = f[len(prefix):]
            if rest:
                items.add(rest.split('/')[0])
                
    print(" ".join(sorted(items)) if items else "")
    return True

def resolve_path(cwd, target):
    """Разрешает абсолютный путь относительно текущего каталога."""
    if target == '/':
        return '/'
        
    parts = [p for p in cwd.split('/') if p]
    for part in target.split('/'):
        if part == '..':
            if parts: parts.pop()
        elif part and part != '.':
            parts.append(part)
            
    return '/' + '/'.join(parts)

def is_dir(path, all_files):
    """Проверяет, существует ли такая директория в архиве."""
    if path == '/': 
        return True
    prefix = path.lstrip('/') + '/'
    return any(f.startswith(prefix) for f in all_files)

def cmd_cd(args, state):
    """Смена текущей директории."""
    if len(args) > 1:
        print("Ошибка: cd ожидает не более 1 аргумента")
        return False
    if not args:
        return True
        
    new_path = resolve_path(state['cwd'], args[0])
    if is_dir(new_path, state['files']):
        state['cwd'] = new_path
        return True
    else:
        print(f"Ошибка: директория '{args[0]}' не найдена")
        return False

def cmd_conf_dump(config):
    """Вывод параметров конфигурации."""
    for key, value in config.items():
        print(f"{key}={value}")
    return True

def execute_command(command, args, config, state):
    """Маршрутизатор команд."""
    if command == "exit":
        return True, False
    elif command == "ls":
        return cmd_ls(args, state), True
    elif command == "cd":
        return cmd_cd(args, state), True
    elif command == "conf-dump":
        return cmd_conf_dump(config), True
    
    print(f"Ошибка: неизвестная команда '{command}'")
    return False, True

def run_script(script_path, config, state, vfs_name):
    """Построчное исполнение стартового скрипта."""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                print(f"{vfs_name}:{state['cwd']} $ {line}")
                try:
                    parsed = shlex.split(line)
                    success, _ = execute_command(parsed[0], parsed[1:], config, state)
                    if not success:
                        print(f"Ошибка исполнения скрипта на строке: {line}")
                        break
                except ValueError as e:
                    print(f"Ошибка синтаксиса в скрипте: {e}")
                    break
    except FileNotFoundError:
        print(f"Ошибка: скрипт '{script_path}' не найден.")

def run_repl(config, state, vfs_name):
    """Интерактивный цикл ввода."""
    print("Эмулятор запущен. Введите 'exit' для выхода.")
    while True:
        try:
            prompt = f"{vfs_name}:{state['cwd']} $ "
            user_input = input(prompt).strip()
            if not user_input: continue
            
            parsed = shlex.split(user_input)
            _, keep_running = execute_command(parsed[0], parsed[1:], config, state)
            if not keep_running: break
        except ValueError as e:
            print(f"Ошибка синтаксиса: {e}")
        except (EOFError, KeyboardInterrupt):
            print("\nВыход...")
            break

def main():
    """Точка входа в программу."""
    config = parse_args()
    print_debug_config(config)
    
    # Инициализация состояния VFS
    files = load_vfs(config["vfs_path"])
    state = {"cwd": "/", "files": files}
    vfs_name = "vfs"
    
    if config["script_path"]:
        run_script(config["script_path"], config, state, vfs_name)
        
    run_repl(config, state, vfs_name)

if __name__ == "__main__":
    main()