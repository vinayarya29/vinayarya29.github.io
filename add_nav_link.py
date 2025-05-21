import sys
import os
from bs4 import BeautifulSoup

def add_cv_navigation_link(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        nav_ul = soup.find('nav', id='nav').find('ul')
        if not nav_ul:
            print(f"Error: Navigation <ul> not found in {filepath}", file=sys.stderr)
            return False

        # Determine the correct path to cv.html
        # os.path.dirname(filepath) gives the directory of the current file.
        # If it's 'research', then cv.html is one level up.
        is_in_research_subdir = os.path.basename(os.path.dirname(filepath)) == 'research'
        cv_href = "../cv.html" if is_in_research_subdir else "cv.html"
        
        # Check if CV link already exists
        for li in nav_ul.find_all('li'):
            a_tag = li.find('a')
            if a_tag and a_tag.has_attr('href') and cv_href in a_tag['href']:
                if a_tag.span and a_tag.span.string == "CV":
                    print(f"Info: CV link already exists in {filepath}. Skipping.", file=sys.stdout)
                    return True # Link already exists

        # Create the new CV list item
        cv_li = soup.new_tag('li')
        cv_a = soup.new_tag('a', class_="icon solid fa-file-text", href=cv_href) # fa-file-text is a guess, adjust if needed
        cv_span = soup.new_tag('span')
        cv_span.string = "CV"
        cv_a.append(cv_span)
        cv_li.append(cv_a)

        # Insert the new link after "Publications" or "Research"
        # Trying to insert after "Publications" first
        publications_li = None
        research_li = None

        for li_tag in nav_ul.find_all('li', recursive=False): # only direct children
            a_tag = li_tag.find('a')
            if a_tag and a_tag.span:
                if a_tag.span.string == "Publications":
                    publications_li = li_tag
                    break 
                elif a_tag.span.string == "Research":
                    research_li = li_tag
        
        inserted = False
        if publications_li:
            publications_li.insert_after(cv_li)
            inserted = True
        elif research_li: # If no "Publications", insert after "Research"
            research_li.insert_after(cv_li)
            inserted = True
        else: # Fallback: append to the end of the list
            nav_ul.append(cv_li)
            inserted = True
            print(f"Warning: Could not find 'Publications' or 'Research' link in {filepath}. Appended CV link to end.", file=sys.stderr)

        if not inserted: # Should not happen with append fallback
             print(f"Error: Failed to insert CV link in {filepath} using any method.", file=sys.stderr)
             return False


        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True

    except Exception as e:
        print(f"An error occurred while processing {filepath}: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python add_nav_link.py <html_filepath>", file=sys.stderr)
        sys.exit(1)
    
    filepath_to_modify = sys.argv[1]
    if add_cv_navigation_link(filepath_to_modify):
        print(f"{filepath_to_modify} updated successfully with CV link.")
    else:
        print(f"Failed to update {filepath_to_modify}.", file=sys.stderr)
        sys.exit(1)
