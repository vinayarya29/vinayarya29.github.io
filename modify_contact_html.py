import sys
from bs4 import BeautifulSoup

def update_contact_html_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # Find the <div id="content">
        content_div = soup.find('div', id='content')
        
        if content_div:
            # Create the new paragraph
            new_paragraph_html = "<p><i>Please review the contact details on this page and provide any necessary updates.</i></p>"
            new_paragraph_soup = BeautifulSoup(new_paragraph_html, 'html.parser').p
            
            if new_paragraph_soup:
                # Insert the new paragraph at the beginning of the div's content
                content_div.insert(0, new_paragraph_soup)
            else:
                print(f"Error: Could not parse the new paragraph HTML for {filepath}", file=sys.stderr)
                return False
        else:
            print(f"Error: <div id='content'> not found in {filepath}", file=sys.stderr)
            return False

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True

    except Exception as e:
        print(f"An error occurred in update_contact_html_file: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if update_contact_html_file('contact.html'):
        print("contact.html updated successfully.")
    else:
        print("Failed to update contact.html.", file=sys.stderr)
        sys.exit(1)
