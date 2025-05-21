import sys
from bs4 import BeautifulSoup

def update_upcoming_html_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # --- Update "Upcoming" section ---
        # The structure in upcoming.html might be just a <p> inside a <section> inside <main>
        # Let's find the <main> tag first
        main_tag = soup.find('main')
        if not main_tag:
            # Fallback: if no <main>, try to find a common container or body
            main_tag = soup.body 
            if not main_tag:
                print(f"Error: Could not find a suitable main content area in {filepath}", file=sys.stderr)
                return False

        # The subtask implies there's an "Upcoming" section.
        # It's currently a <p> directly within a <section>. Let's find that <p>.
        # A more robust way would be to add an <h2>Upcoming</h2> and then a <p>,
        # but we need to match the current structure.
        # The current structure is <section><p>We are updating...</p></section>
        
        # Find all <p> tags within <section> tags that are children of <main_tag>
        target_p = None
        if main_tag:
            sections = main_tag.find_all('section', recursive=False) # direct children sections
            for section in sections:
                # Check for a <p> tag that contains the specific old placeholder text.
                # This is more robust than assuming it's the *only* <p> tag.
                p_tag = section.find('p', string="We are updating the work progress as divided in various themes.")
                if p_tag:
                    target_p = p_tag
                    break
        
        if target_p:
            target_p.string = "[Placeholder for user to list upcoming conferences, workshops, talks, or other events they will be participating in or that are relevant to their research.]"
        else:
            # If the specific placeholder isn't found, we need to decide what to do.
            # The task implies this structure exists.
            # Let's check if there's any <p> in the first <section> of <main> as a fallback.
            if main_tag and main_tag.section and main_tag.section.p:
                main_tag.section.p.string = "[Placeholder for user to list upcoming conferences, workshops, talks, or other events they will be participating in or that are relevant to their research.]"
                print(f"Warning: Original placeholder text in 'Upcoming' section not found or structure differs. Updated the first <p> in the first <section> of <main> in {filepath}", file=sys.stderr)
            else:
                print(f"Error: Could not find the target paragraph in 'Upcoming' section in {filepath}. No changes made.", file=sys.stderr)
                return False


        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True

    except Exception as e:
        print(f"An error occurred in update_upcoming_html_file: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if update_upcoming_html_file('research/upcoming.html'):
        print("research/upcoming.html updated successfully.")
    else:
        print("Failed to update research/upcoming.html.", file=sys.stderr)
        sys.exit(1)
