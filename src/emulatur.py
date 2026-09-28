import shlex
import sys

def cmd_ls(args):
    print("Вызвана команда: ls")
    print(f"Аргументы: {args}")

def cmd_cd(args):
    if len(args) > 1:
        print(f"Ошибка: cd принимает не более одного аргумента, передано {len(args)}")
        return
    print("Вызвана команда: cd")
    print(f"Аргументы: {args}")

def execute_command(command, args):
    if command == "exit":
        return False
    elif command == "ls":
        cmd_ls(args)
    elif command == "cd":
        cmd_cd(args)
    else:
        print(f"Ошибка: неизвестная команда '{command}'")
    return True

def main():
    vfs_name = "vfs"
    print("Эмулятор оболочки ОС запущен. Для выхода введите 'exit'.")

    while True:
        try:
            user_input = input(f"{vfs_name}:/ $ ").strip()
            if not user_input:
                continue
            
            parsed_input = shlex.split(user_input)
            command = parsed_input[0]
            args = parsed_input[1:]

            if not execute_command(command, args):
                break
                
        except ValueError as e:
            print(f"Ошибка синтаксиса: {e} (пропущена закрывающая кавычка)")
        except EOFError:
            print("\nВыход...")
            break
        except KeyboardInterrupt:
            print("\nДля выхода введите 'exit'")

if __name__ == "__main__":
    main()