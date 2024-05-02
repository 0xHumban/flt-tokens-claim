import os

from flt import *

private_key = os.getenv("PRIVATE_KEY")
contract_address = "0x6081d7F04a8c31e929f25152d4ad37c83638C62b"
http_provider_url = "https://eth-mainnet.public.blastapi.io"



def main_menu(flt):

    print("\nUSER INFORMATION:")
    flt.show_flt_drop_balance()
    flt.show_unlock_time()
    print("\nMenu:")
    print("1. Perform transfer")
    print("2. Quit")

    choice = input("Enter your choice: ")

    if choice == "1":
        confirm = input("Are you sure you want to perform the transfer? (Y/N): ")
        if confirm.upper() == "Y" or choice.upper() == "YES":
            flt.perform_transfer_to_yourself()
    elif choice == "2":
        print("Goodbye!")
        return
    else:
        print("Invalid choice. Please select a valid option.")

    main_menu(flt)


def check_env_variable(env_var):
    return env_var is not  None


if __name__ == "__main__":
    if not check_env_variable(private_key):
        print("Please set the env variable \"PRIVATE_KEY\"")
        exit(1)
    flt = FLT(http_provider_url, contract_address, private_key)
    print("*"*35)
    print("\nClaim $FLT tokens in your terminal \n")
    print("*"*35)
    flt.check_connexion()
    main_menu(flt)
