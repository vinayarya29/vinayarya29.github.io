import sys
from bs4 import BeautifulSoup

def create_placeholder_section(soup, title_text, placeholder_texts):
    """Helper function to create a themed section with placeholders."""
    section_div = soup.new_tag('div', class_='research-theme') # Using a div for grouping
    
    title_h3 = soup.new_tag('h3')
    title_h3.string = title_text
    section_div.append(title_h3)
    
    for key, placeholder in placeholder_texts.items():
        sub_title_h4 = soup.new_tag('h4')
        sub_title_h4.string = key.replace("_", " ") # Make titles more readable
        section_div.append(sub_title_h4)
        
        p_tag = soup.new_tag('p')
        p_tag.string = placeholder
        section_div.append(p_tag)
        
    return section_div

def update_research_html_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # Locate the main content section. 
        # Assuming the main content is within a <section> tag that contains <h2>Research Themes</h2>
        h2_research_themes = soup.find('h2', string='Research Themes')
        if not h2_research_themes:
            print("Error: <h2>Research Themes</h2> not found.", file=sys.stderr)
            return False
        
        main_content_section = h2_research_themes.find_parent('section')
        if not main_content_section:
            # Fallback: sometimes the h2 might be directly in main or a similar container
            main_content_section = h2_research_themes.find_parent() 
            if not main_content_section:
                 print("Error: Main content section for 'Research Themes' not found.", file=sys.stderr)
                 return False

        # Remove the old "Fluid flow at the Interfaces" paragraph
        old_fluid_flow_p = main_content_section.find('p', string='Fluid flow at the Interfaces')
        if old_fluid_flow_p:
            old_fluid_flow_p.decompose()
        else:
            # If the specific <p> is not found, we continue, as the goal is to add new content.
            # It might have been removed or changed.
            print("Warning: Original 'Fluid flow at the Interfaces' paragraph not found. Proceeding to add new structure.", file=sys.stderr)

        # 1. Add structured layout for "Fluid flow at the Interfaces"
        fluid_flow_placeholders = {
            "Detailed_Description": "[Placeholder for user to provide content]",
            "Ongoing_Projects": "[Placeholder for user to provide content]",
            "Methodologies_Used": "[Placeholder for user to provide content]",
            "Key_Findings": "[Placeholder for user to provide content]",
            "Relevant_Publications": "[Placeholder for user to provide links or text]"
        }
        fluid_flow_section_div = create_placeholder_section(soup, "Fluid flow at the Interfaces", fluid_flow_placeholders)
        
        # Insert the new section after the H2 tag
        h2_research_themes.insert_after(fluid_flow_section_div)
        
        # 2. Add "Other Research Areas" section
        other_areas_h2 = soup.new_tag('h2')
        other_areas_h2.string = "Other Research Areas"
        
        other_areas_p = soup.new_tag('p')
        other_areas_p.string = "[Placeholder for user to describe other research interests or themes, if any]"
        
        # Append this new section to the main_content_section
        # Or, if main_content_section is too broad, find a more specific parent,
        # for now, we'll append it where the old p tag was, or after the fluid_flow_section
        fluid_flow_section_div.insert_after(other_areas_h2)
        other_areas_h2.insert_after(other_areas_p)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True

    except Exception as e:
        print(f"An error occurred in update_research_html_file: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if update_research_html_file('research.html'):
        print("research.html updated successfully.")
    else:
        print("Failed to update research.html.", file=sys.stderr)
        sys.exit(1)
