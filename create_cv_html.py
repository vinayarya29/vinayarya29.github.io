import sys
from bs4 import BeautifulSoup

def create_cv_page(template_filepath, new_filepath):
    try:
        with open(template_filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # 1. Update Title
        title_tag = soup.find('title')
        if title_tag:
            title_tag.string = "Vinay Arya - CV"
        else:
            print(f"Warning: <title> tag not found in template {template_filepath}", file=sys.stderr)
            # Create title if not exists
            head_tag = soup.head
            if not head_tag: # Should not happen in valid HTML5
                head_tag = soup.new_tag('head')
                soup.html.insert(0, head_tag)
            new_title_tag = soup.new_tag('title')
            new_title_tag.string = "Vinay Arya - CV"
            head_tag.append(new_title_tag)

        # 2. Clear existing main content and add CV specific content
        #    The structure of contact.html's main content is:
        #    <section id="main"> <div class="container"> <div id="content"> ... </div> </div> </section>
        #    Plus other <section> tags for map and contact details. We want to simplify for CV.
        
        main_section = soup.find('section', id='main')
        if not main_section:
            print(f"Error: <section id='main'> not found in template {template_filepath}. Creating one.", file=sys.stderr)
            # Create main section if not exists, and place it after header or as child of page-wrapper
            page_wrapper = soup.find('div', id='page-wrapper')
            header_section = soup.find('section', id='header')
            main_section = soup.new_tag('section', id='main')
            if page_wrapper:
                if header_section:
                    header_section.insert_after(main_section)
                else: # Should not happen
                    page_wrapper.insert(1, main_section) # Insert after header usually
            else: # Should not happen
                soup.body.insert(1, main_section)


        container_div = main_section.find('div', class_='container')
        if not container_div:
            container_div = soup.new_tag('div', class_='container')
            main_section.clear() # Clear previous content if any
            main_section.append(container_div)
        else:
            # Clear existing content within the container of <section id="main">
            container_div.clear()

        # Add new CV content: <h2> and <p>
        h2_cv = soup.new_tag('h2')
        h2_cv.string = "Curriculum Vitae"
        container_div.append(h2_cv)

        p_cv_placeholder = soup.new_tag('p')
        p_cv_placeholder.string = "[Placeholder for user to add their CV content. This can be pasted as text, or you can provide a link to a PDF document.]"
        container_div.append(p_cv_placeholder)
        
        # Remove other sections that might have been copied from contact.html template (like map, specific contact details layout)
        # This depends on the exact structure of contact.html. 
        # The current contact.html has additional <section> tags after <section id="main">.
        # We will remove all sibling <section> tags of main_section if they are not 'header' or 'footer'
        all_sections = soup.find_all('section', recursive=False) # Top-level sections
        if soup.body and soup.body.find('div', id='page-wrapper'):
             all_sections = soup.find('div', id='page-wrapper').find_all('section', recursive=False)


        for section in all_sections:
            if section.get('id') not in ['header', 'main', 'footer', 'banner']: # Keep banner if it exists
                section.decompose()


        # 3. Update Navigation Links in the new cv.html
        nav_ul = soup.find('nav', id='nav').find('ul')
        if nav_ul:
            # Adjust existing links if necessary (paths should be fine if cv.html is at root)
            # Add the "CV" link to its own nav bar, make it active or distinct if desired
            
            # First, ensure all existing links are correct for a root file
            for li in nav_ul.find_all('li'):
                a_tag = li.find('a')
                if a_tag and a_tag.has_attr('href'):
                    href = a_tag['href']
                    if href.startswith('../'): # Should not be needed if template is a root file
                        a_tag['href'] = href.replace('../', '')
                    elif 'research/' in href and not href.startswith('research/'): # e.g. from a subpage
                         a_tag['href'] = href.split('research/')[1] # make it relative to root
                         if not href.startswith('research/'): # if it was ../research/PMRF.html
                             a_tag['href'] = 'research/' + a_tag['href']


            # Add new CV link
            cv_li = soup.new_tag('li')
            cv_a = soup.new_tag('a', class_="icon solid fa-file-text", href="cv.html")
            cv_span = soup.new_tag('span')
            cv_span.string = "CV"
            cv_a.append(cv_span)
            cv_li.append(cv_a)

            # Find "Publications" or "Research" to insert "CV" after
            inserted = False
            for li_tag in nav_ul.find_all('li'):
                a_tag = li_tag.find('a')
                if a_tag and a_tag.span:
                    if a_tag.span.string == "Publications":
                        li_tag.insert_after(cv_li)
                        inserted = True
                        break
            if not inserted: # Fallback: append to end or after research
                 for li_tag in nav_ul.find_all('li'):
                    a_tag = li_tag.find('a')
                    if a_tag and a_tag.span and a_tag.span.string == "Research":
                        li_tag.insert_after(cv_li)
                        inserted = True
                        break
            if not inserted: # Fallback: append to the end
                nav_ul.append(cv_li)
        else:
            print("Warning: Navigation <ul> not found. CV link not added to cv.html itself.", file=sys.stderr)


        with open(new_filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True

    except Exception as e:
        print(f"An error occurred in create_cv_page: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if create_cv_page('contact.html', 'cv.html'): # Using contact.html as template
        print("cv.html created successfully.")
    else:
        print("Failed to create cv.html.", file=sys.stderr)
        sys.exit(1)
