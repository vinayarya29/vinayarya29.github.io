import sys
from bs4 import BeautifulSoup

def update_publications_html_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # --- Update Conference Publications ---
        h2_conference = soup.find('h2', string='Conference Publications')
        if h2_conference:
            # Find the specific paragraph to replace
            old_p_conference = h2_conference.find_next_sibling('p')
            if old_p_conference and old_p_conference.string == "We are updating the work progress as divided in various themes.":
                old_p_conference.string = "[Placeholder for user to list conference publications. Please include title, conference name, date, and a weblink if available for each.]"
            elif old_p_conference:
                # If the string doesn't match, it might have been changed or is not the expected one.
                # For safety, we could choose to not change it or log a more specific warning.
                # However, the task implies this specific placeholder is present.
                # For now, we'll assume if a 'p' is there, it's the one to change.
                old_p_conference.string = "[Placeholder for user to list conference publications. Please include title, conference name, date, and a weblink if available for each.]"
                print("Warning: Conference publications placeholder text was not the expected 'We are updating...'. It has been overwritten.", file=sys.stderr)
            else:
                # If no <p> tag is found, create one
                new_p_conference = soup.new_tag('p')
                new_p_conference.string = "[Placeholder for user to list conference publications. Please include title, conference name, date, and a weblink if available for each.]"
                h2_conference.insert_after(new_p_conference)
                print("Warning: No existing placeholder paragraph found for Conference Publications. A new one was created.", file=sys.stderr)
        else:
            print("Error: <h2>Conference Publications</h2> not found.", file=sys.stderr)
            return False

        # --- Update Workshop Talks ---
        h2_workshop = soup.find('h2', string='Workshop Talks')
        if h2_workshop:
            # Find the specific paragraph to replace
            old_p_workshop = h2_workshop.find_next_sibling('p')
            if old_p_workshop and old_p_workshop.string == "We are updating the work progress as divided in various themes.":
                old_p_workshop.string = "[Placeholder for user to list workshop talks. Please include title, event name, date, and a weblink if available for each.]"
            elif old_p_workshop:
                old_p_workshop.string = "[Placeholder for user to list workshop talks. Please include title, event name, date, and a weblink if available for each.]"
                print("Warning: Workshop talks placeholder text was not the expected 'We are updating...'. It has been overwritten.", file=sys.stderr)
            else:
                # If no <p> tag is found, create one
                new_p_workshop = soup.new_tag('p')
                new_p_workshop.string = "[Placeholder for user to list workshop talks. Please include title, event name, date, and a weblink if available for each.]"
                h2_workshop.insert_after(new_p_workshop)
                print("Warning: No existing placeholder paragraph found for Workshop Talks. A new one was created.", file=sys.stderr)

        else:
            print("Error: <h2>Workshop Talks</h2> not found.", file=sys.stderr)
            return False

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if update_publications_html_file('publications.html'):
        print("publications.html updated successfully.")
    else:
        print("Failed to update publications.html.", file=sys.stderr)
        sys.exit(1)
