import time
from core.auth import register, login
from core.storage import save_password, get_password, list_labels, delete_password
from core.password_gen import generate_strong_password


def main():
    print("=" * 40)
    print("   ?? Data Vault - Offline Password Manager")
    print("=" * 40)

    print("\n1. Register")
    print("2. Login")
    choice = input("Choose: ").strip()

    if choice == "1":
        master = input("Set master password: ").strip()
        register(master)

    elif choice == "2":
        master = input("Enter master password: ").strip()
        if not login(master):
            print("? Wrong password! Access denied.")
            return
        print("? Login successful!")

    else:
        print("Invalid choice!")
        return

    while True:
        print("\n" + "=" * 40)
        print("1. Save a password")
        print("2. Get a password")
        print("3. List all labels")
        print("4. Delete a password")
        print("5. Generate strong password")
        print("6. Exit")
        print("=" * 40)

        action = input("Choose: ").strip()

        if action == "1":
            label = input("Label (e.g. gmail): ").strip()
            pwd = input("Password to save: ").strip()
            save_password(master, label, pwd)

        elif action == "2":
            label = input("Label to retrieve: ").strip()
            try:
                pwd = get_password(master, label)
                print(f"?? Password: {pwd}")
                print("? Hiding in 30 seconds...")
                time.sleep(30)
                print("?? Password hidden!")
            except KeyError as e:
                print(e)

        elif action == "3":
            labels = list_labels()
            if labels:
                print("?? Saved labels:", labels)
            else:
                print("No passwords saved yet!")

        elif action == "4":
            label = input("Label to delete: ").strip()
            try:
                delete_password(label)
            except KeyError as e:
                print(e)

        elif action == "5":
            length = input("Password length (default 16): ").strip()
            length = int(length) if length else 16
            print("?? Generated:", generate_strong_password(length))

        elif action == "6":
            print("?? Goodbye!")
            break

        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()
