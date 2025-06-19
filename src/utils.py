from random import choice

def randomoji():
    return choice(["&#127814;",
                   "&#127798;",
                   "&#127826;",
                   "&#127825;",
                   "&#127853;",
                   "&#129373;",
                   "&#129361;",
                   "&#129473;",
                   "&#129375;",
                   "&#127817;",
                   "&#127849;",
                   "&#127820;",
                   "&#127805;",
                   "&#127852;",
                   "&#127815;",
                   "&#127822;",
                   "&#127789;"])

def randomoji_link(ref):
    return f"""
           <p style="font-size:5em; text-align:center;">
            <a href="{ref}" style="text-decoration: none">
             {randomoji()}
            </a></p>"""

def randomoji_control(ref, control):
    return f"""
           <p style="font-size:5em; text-align:center;">
            <a href="{ref}" style="text-decoration: none">
             <span class="emoji">{randomoji()}</span>
             <span class="control">{control}</span>
            </a></p>"""

def options(input_list):
    return "".join(f"<option value=\"{input}\"> {input.capitalize()} </option>" for input in input_list)

def datalist(id, input_list, selected = []):
    datalist = "<datalist id=\"" + id + "\">\n"
    for input in input_list:
        s = "selected" if input in selected else ""
        datalist += f"<option {s} value=\"{input.capitalize()}\">{input.capitalize()}</option>\n"
    datalist += "</datalist>"
    return datalist
