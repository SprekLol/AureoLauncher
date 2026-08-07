def get_text_font(style="normal"):
    if style == "title":
        return ("Segoe UI", 18, "bold")
    elif style == "subtitle":
        return ("Segoe UI", 14, "bold")
    elif style == "section_title":
        return ("Segoe UI", 12, "bold")
    elif style == "normal":
        return ("Segoe UI", 10)
    elif style == "small":
        return ("Segoe UI", 9)
    else:
        return ("Segoe UI", 10)
