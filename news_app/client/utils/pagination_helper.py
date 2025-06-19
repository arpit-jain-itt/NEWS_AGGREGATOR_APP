from typing import Callable, List, Any


def cli_paginate_items(
    fetch_fn: Callable[[int, int], List[Any]],
    title: str = "Items",
    per_page: int = 5,
    on_select: Callable[[Any], None] = None,
    display_fn: Callable[[Any, int], None] = None,
) -> None:

    page = 1

    while True:
        offset = (page - 1) * per_page
        items = fetch_fn(per_page, offset)

        if not items:
            print("No items found.")
            return

        print(f"\n--- {title} (Page {page}) ---")
        for idx, item in enumerate(items, start=offset + 1):
            if display_fn:
                display_fn(item, idx)
            else:
                print(f"{idx}. {item}")

        choice = (
            input(
                "\nOptions: [Enter number of article to view its details | n: Next | p: Prev | b: Back]: "
            )
            .strip()
            .lower()
        )

        if choice == "n":
            page += 1
        elif choice == "p" and page > 1:
            page -= 1
        elif choice == "b":
            return
        elif choice.isdigit():
            global_index = int(choice)
            if offset + 1 <= global_index <= offset + len(items):
                if on_select:
                    on_select(items[global_index - offset - 1])
            else:
                print("Invalid item number.")
        else:
            print("Invalid choice.")
