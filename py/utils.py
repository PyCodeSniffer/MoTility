from textual.widgets import Button

def create_smart_button(text: str, button_id: str, shortcut_dict: dict) -> Button:
    display_text = text
    if "&" in text:
        idx = text.find("&")
        char = text[idx + 1]
        display_text = text.replace(f"&{char}", f"[yellow]{char}[/yellow]")
        shortcut_dict[char.lower()] = button_id
    
    btn = Button(display_text, id=button_id)
    btn.styles.min_width = 35
    btn.styles.height = 5
    return btn
