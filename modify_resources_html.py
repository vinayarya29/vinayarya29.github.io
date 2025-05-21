import sys
from bs4 import BeautifulSoup

def update_resources_html_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        sections_to_update = {
            "Resources": "[Placeholder for user to add links to general resources, software, or tools relevant to their research area.]",
            "Gromacs Tutorials": "[Placeholder for user to add links to GROMACS tutorials they have created or found useful, especially concerning fluid flow and heat transfer in nanochannels.]",
            "CFD Tutorials": "[Placeholder for user to add links to CFD tutorials they have created or found useful, especially concerning fluid flow and heat transfer in microchannels.]"
        }

        all_sections_found = True
        for section_title, new_text in sections_to_update.items():
            h2_section = soup.find('h2', string=section_title)
            if h2_section:
                p_section = h2_section.find_next_sibling('p')
                if p_section:
                    p_section.string = new_text
                else:
                    print(f"Warning: No <p> tag found immediately after '{section_title}' <h2> in {filepath}", file=sys.stderr)
                    # Optionally create the <p> if it's missing
                    new_p = soup.new_tag('p')
                    new_p.string = new_text
                    h2_section.insert_after(new_p)
            else:
                print(f"Error: <h2>{section_title}</h2> not found in {filepath}", file=sys.stderr)
                all_sections_found = False
        
        if not all_sections_found:
            # Decide if this constitutes overall failure or partial success
            # For this task, if any h2 is missing, it's an issue.
            # However, the script will still attempt to update the sections it *does* find.
            pass # Or return False if strict adherence is needed

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True

    except Exception as e:
        print(f"An error occurred in update_resources_html_file: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if update_resources_html_file('research/resources.html'):
        print("research/resources.html updated successfully.")
    else:
        print("Failed to update research/resources.html.", file=sys.stderr)
        sys.exit(1)
